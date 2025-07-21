import os
import json
import uuid
import shutil
from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
from werkzeug.utils import secure_filename
from app import app
from utils import validate_cpf, format_phone, get_motoristas, save_motorista, get_motorista_by_id, update_motorista, create_backup

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Página inicial com estatísticas"""
    motoristas = get_motoristas()
    total_motoristas = len(motoristas)
    
    # Contar documentos vencidos
    documentos_vencidos = 0
    documentos_vencendo = 0
    hoje = datetime.now().date()
    
    for motorista in motoristas:
        if motorista.get('validade_cnh'):
            try:
                validade_cnh = datetime.strptime(motorista['validade_cnh'], '%Y-%m-%d').date()
                if validade_cnh < hoje:
                    documentos_vencidos += 1
                elif validade_cnh <= hoje + timedelta(days=30):
                    documentos_vencendo += 1
            except ValueError:
                pass
                
        if motorista.get('validade_curso'):
            try:
                validade_curso = datetime.strptime(motorista['validade_curso'], '%Y-%m-%d').date()
                if validade_curso < hoje:
                    documentos_vencidos += 1
                elif validade_curso <= hoje + timedelta(days=30):
                    documentos_vencendo += 1
            except ValueError:
                pass
    
    stats = {
        'total_motoristas': total_motoristas,
        'documentos_vencidos': documentos_vencidos,
        'documentos_vencendo': documentos_vencendo
    }
    
    return render_template('index.html', stats=stats)

@app.route('/cadastro')
def cadastro():
    """Página de cadastro de motorista"""
    return render_template('cadastro.html')

@app.route('/cadastro', methods=['POST'])
def cadastro_post():
    """Processar cadastro de motorista"""
    try:
        # Validar CPF
        cpf = request.form.get('cpf', '').replace('.', '').replace('-', '')
        if not validate_cpf(cpf):
            flash('CPF inválido', 'error')
            return redirect(url_for('cadastro'))
        
        # Verificar se CPF já existe
        motoristas = get_motoristas()
        for motorista in motoristas:
            if motorista.get('cpf') == cpf:
                flash('CPF já cadastrado', 'error')
                return redirect(url_for('cadastro'))
        
        # Criar ID único
        motorista_id = str(uuid.uuid4())
        
        # Criar pasta do motorista
        motorista_folder = os.path.join(app.config['UPLOAD_FOLDER'], motorista_id)
        os.makedirs(motorista_folder, exist_ok=True)
        os.makedirs(os.path.join(motorista_folder, 'documentos'), exist_ok=True)
        os.makedirs(os.path.join(motorista_folder, 'holerites'), exist_ok=True)
        
        # Dados do motorista
        motorista = {
            'id': motorista_id,
            'nome': request.form.get('nome'),
            'data_nascimento': request.form.get('data_nascimento'),
            'cpf': cpf,
            'celular': format_phone(request.form.get('celular')),
            'tipo_vinculo': request.form.get('tipo_vinculo'),
            'validade_cnh': request.form.get('validade_cnh'),
            'validade_curso': request.form.get('validade_curso'),
            'data_cadastro': datetime.now().isoformat(),
            'status': 'ativo',
            'arquivos': {}
        }
        
        # Upload da foto
        if 'foto' in request.files:
            foto = request.files['foto']
            if foto and foto.filename and allowed_file(foto.filename):
                # Criar nome único para foto
                extensao = foto.filename.rsplit('.', 1)[1].lower()
                filename = f"foto_{motorista_id}.{extensao}"
                foto_path = os.path.join(motorista_folder, filename)
                foto.save(foto_path)
                motorista['arquivos']['foto'] = filename
                app.logger.info(f"Foto salva: {foto_path}")
            else:
                app.logger.warning("Foto não enviada ou formato inválido")
        
        # Upload dos documentos
        documentos = ['cnh', 'curso_passageiro', 'comprovante_residencia']
        for doc in documentos:
            if doc in request.files:
                file = request.files[doc]
                if file and file.filename and allowed_file(file.filename):
                    extensao = file.filename.rsplit('.', 1)[1].lower()
                    filename = f"{doc}_{motorista_id}.{extensao}"
                    file_path = os.path.join(motorista_folder, 'documentos', filename)
                    file.save(file_path)
                    motorista['arquivos'][doc] = filename
                    app.logger.info(f"Documento {doc} salvo: {file_path}")
                else:
                    app.logger.warning(f"Documento {doc} não enviado ou formato inválido")
        
        # Salvar motorista
        save_motorista(motorista)
        
        flash('Motorista cadastrado com sucesso!', 'success')
        return redirect(url_for('motorista', id=motorista_id))
        
    except Exception as e:
        app.logger.error(f"Erro ao cadastrar motorista: {str(e)}")
        flash('Erro ao cadastrar motorista. Tente novamente.', 'error')
        return redirect(url_for('cadastro'))

@app.route('/motorista/<id>')
def motorista(id):
    """Página de detalhes do motorista"""
    motorista = get_motorista_by_id(id)
    if not motorista:
        flash('Motorista não encontrado', 'error')
        return redirect(url_for('index'))
    
    # Verificar vencimentos
    hoje = datetime.now().date()
    alertas = []
    
    if motorista.get('validade_cnh'):
        try:
            validade_cnh = datetime.strptime(motorista['validade_cnh'], '%Y-%m-%d').date()
            if validade_cnh < hoje:
                alertas.append(('CNH vencida', 'danger'))
            elif validade_cnh <= hoje + timedelta(days=30):
                alertas.append(('CNH vence em breve', 'warning'))
        except ValueError:
            pass
    
    if motorista.get('validade_curso'):
        try:
            validade_curso = datetime.strptime(motorista['validade_curso'], '%Y-%m-%d').date()
            if validade_curso < hoje:
                alertas.append(('Curso vencido', 'danger'))
            elif validade_curso <= hoje + timedelta(days=30):
                alertas.append(('Curso vence em breve', 'warning'))
        except ValueError:
            pass
    
    # Listar holerites
    holerites_folder = os.path.join(app.config['UPLOAD_FOLDER'], id, 'holerites')
    holerites = []
    if os.path.exists(holerites_folder):
        for year_folder in os.listdir(holerites_folder):
            year_path = os.path.join(holerites_folder, year_folder)
            if os.path.isdir(year_path):
                for month_folder in os.listdir(year_path):
                    month_path = os.path.join(year_path, month_folder)
                    if os.path.isdir(month_path):
                        for file in os.listdir(month_path):
                            if file.endswith(('.pdf', '.png', '.jpg', '.jpeg')):
                                holerites.append({
                                    'ano': year_folder,
                                    'mes': month_folder,
                                    'arquivo': file,
                                    'path': os.path.join(year_folder, month_folder, file)
                                })
    
    return render_template('motorista.html', motorista=motorista, alertas=alertas, holerites=holerites)

@app.route('/lista')
def lista():
    """Página de listagem de motoristas"""
    motoristas = get_motoristas()
    
    # Adicionar informações de vencimento
    hoje = datetime.now().date()
    for motorista in motoristas:
        # Garantir que o campo status existe
        if 'status' not in motorista:
            motorista['status'] = 'ativo'
        if 'tipo_vinculo' not in motorista:
            motorista['tipo_vinculo'] = 'registrado'
            
        motorista['status_cnh'] = 'ok'
        motorista['status_curso'] = 'ok'
        
        if motorista.get('validade_cnh'):
            try:
                validade_cnh = datetime.strptime(motorista['validade_cnh'], '%Y-%m-%d').date()
                if validade_cnh < hoje:
                    motorista['status_cnh'] = 'vencido'
                elif validade_cnh <= hoje + timedelta(days=30):
                    motorista['status_cnh'] = 'vencendo'
            except ValueError:
                pass
        
        if motorista.get('validade_curso'):
            try:
                validade_curso = datetime.strptime(motorista['validade_curso'], '%Y-%m-%d').date()
                if validade_curso < hoje:
                    motorista['status_curso'] = 'vencido'
                elif validade_curso <= hoje + timedelta(days=30):
                    motorista['status_curso'] = 'vencendo'
            except ValueError:
                pass
    
    return render_template('lista.html', motoristas=motoristas)

@app.route('/upload_holerite/<id>', methods=['POST'])
def upload_holerite(id):
    """Upload de holerite"""
    try:
        motorista = get_motorista_by_id(id)
        if not motorista:
            return jsonify({'error': 'Motorista não encontrado'}), 404
        
        ano = request.form.get('ano')
        mes = request.form.get('mes')
        
        if not ano or not mes:
            return jsonify({'error': 'Ano e mês são obrigatórios'}), 400
        
        if 'holerite' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['holerite']
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        if file and allowed_file(file.filename):
            # Criar pasta do holerite
            holerite_folder = os.path.join(app.config['UPLOAD_FOLDER'], id, 'holerites', ano, mes)
            os.makedirs(holerite_folder, exist_ok=True)
            
            extensao = file.filename.rsplit('.', 1)[1].lower()
            filename = f"holerite_{ano}_{mes}.{extensao}"
            file_path = os.path.join(holerite_folder, filename)
            file.save(file_path)
            
            app.logger.info(f"Holerite salvo: {file_path}")
            return jsonify({'success': True, 'message': 'Holerite enviado com sucesso!'})
        
        return jsonify({'error': 'Tipo de arquivo não permitido'}), 400
        
    except Exception as e:
        app.logger.error(f"Erro ao fazer upload do holerite: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/download_arquivo/<id>/<tipo>/<arquivo>')
def download_arquivo(id, tipo, arquivo):
    """Download de arquivo"""
    try:
        motorista = get_motorista_by_id(id)
        if not motorista:
            flash('Motorista não encontrado', 'error')
            return redirect(url_for('index'))
        
        if tipo == 'foto':
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], id, arquivo)
        elif tipo == 'documento':
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], id, 'documentos', arquivo)
        elif tipo == 'holerite':
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], id, 'holerites', arquivo)
        else:
            flash('Tipo de arquivo inválido', 'error')
            return redirect(url_for('motorista', id=id))
        
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            flash('Arquivo não encontrado', 'error')
            return redirect(url_for('motorista', id=id))
            
    except Exception as e:
        app.logger.error(f"Erro ao fazer download: {str(e)}")
        flash('Erro ao fazer download do arquivo', 'error')
        return redirect(url_for('motorista', id=id))

@app.route('/backup')
def backup():
    """Criar backup dos dados"""
    try:
        backup_path = create_backup()
        flash('Backup criado com sucesso! O arquivo será baixado automaticamente.', 'success')
        
        # Enviar arquivo e limpar após download
        def remove_file(response):
            try:
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                    app.logger.info(f"Arquivo de backup removido: {backup_path}")
            except Exception as e:
                app.logger.error(f"Erro ao remover arquivo de backup: {str(e)}")
            return response
        
        return send_file(backup_path, as_attachment=True, download_name=os.path.basename(backup_path))
    except Exception as e:
        app.logger.error(f"Erro ao criar backup: {str(e)}")
        flash('Erro ao criar backup', 'error')
        return redirect(url_for('index'))

@app.route('/buscar')
def buscar():
    """Buscar motoristas"""
    query = request.args.get('q', '').lower()
    motoristas = get_motoristas()
    
    if query:
        motoristas = [m for m in motoristas if 
                     query in m.get('nome', '').lower() or 
                     query in m.get('cpf', '')]
    
    return jsonify(motoristas)

@app.route('/toggle_status/<id>', methods=['POST'])
def toggle_status(id):
    """Alterar status do motorista (ativo/inativo)"""
    try:
        motorista = get_motorista_by_id(id)
        if not motorista:
            return jsonify({'error': 'Motorista não encontrado'}), 404
        
        data = request.get_json()
        novo_status = data.get('status')
        
        if novo_status not in ['ativo', 'inativo']:
            return jsonify({'error': 'Status inválido'}), 400
        
        motorista['status'] = novo_status
        
        if save_motorista(motorista):
            acao = 'ativado' if novo_status == 'ativo' else 'desativado'
            app.logger.info(f"Motorista {motorista['nome']} {acao}")
            return jsonify({'success': True, 'message': f'Motorista {acao} com sucesso!'})
        else:
            return jsonify({'error': 'Erro ao salvar alterações'}), 500
            
    except Exception as e:
        app.logger.error(f"Erro ao alterar status: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/delete_motorista/<id>', methods=['DELETE'])
def delete_motorista(id):
    """Excluir motorista permanentemente"""
    try:
        motorista = get_motorista_by_id(id)
        if not motorista:
            return jsonify({'error': 'Motorista não encontrado'}), 404
        
        # Excluir arquivos físicos
        motorista_folder = os.path.join(app.config['UPLOAD_FOLDER'], id)
        if os.path.exists(motorista_folder):
            shutil.rmtree(motorista_folder)
            app.logger.info(f"Pasta do motorista excluída: {motorista_folder}")
        
        # Remover do JSON
        motoristas = get_motoristas()
        motoristas = [m for m in motoristas if m['id'] != id]
        
        with open('data/motoristas.json', 'w', encoding='utf-8') as f:
            json.dump(motoristas, f, indent=2, ensure_ascii=False)
        
        app.logger.info(f"Motorista {motorista['nome']} excluído permanentemente")
        return jsonify({'success': True, 'message': 'Motorista excluído com sucesso!'})
        
    except Exception as e:
        app.logger.error(f"Erro ao excluir motorista: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500
