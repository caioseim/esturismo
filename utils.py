import os
import json
import shutil
import re
from datetime import datetime
from app import app

DATA_FILE = 'data/motoristas.json'

def validate_cpf(cpf):
    """Validar CPF brasileiro"""
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    
    # Validar primeiro dígito
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    if int(cpf[9]) != digito1:
        return False
    
    # Validar segundo dígito
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    return int(cpf[10]) == digito2

def format_phone(phone):
    """Formatar telefone brasileiro"""
    phone = re.sub(r'[^0-9]', '', phone)
    if len(phone) == 11:
        return f"({phone[:2]}) {phone[2:7]}-{phone[7:]}"
    elif len(phone) == 10:
        return f"({phone[:2]}) {phone[2:6]}-{phone[6:]}"
    return phone

def get_motoristas():
    """Obter lista de motoristas"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        app.logger.error(f"Erro ao carregar motoristas: {str(e)}")
        return []

def save_motorista(motorista):
    """Salvar motorista"""
    try:
        motoristas = get_motoristas()
        
        # Verificar se é atualização ou novo cadastro
        existing_index = None
        for i, m in enumerate(motoristas):
            if m['id'] == motorista['id']:
                existing_index = i
                break
        
        if existing_index is not None:
            motoristas[existing_index] = motorista
        else:
            motoristas.append(motorista)
        
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(motoristas, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        app.logger.error(f"Erro ao salvar motorista: {str(e)}")
        return False

def get_motorista_by_id(id):
    """Obter motorista por ID"""
    motoristas = get_motoristas()
    for motorista in motoristas:
        if motorista['id'] == id:
            return motorista
    return None

def update_motorista(id, dados):
    """Atualizar motorista"""
    motorista = get_motorista_by_id(id)
    if motorista:
        motorista.update(dados)
        return save_motorista(motorista)
    return False

def create_backup():
    """Criar backup completo dos dados"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"backup_es_turismo_{timestamp}"
        backup_path = f"{backup_name}.zip"
        
        # Criar diretório temporário para o backup
        backup_dir = f"temp_backup_{timestamp}"
        os.makedirs(backup_dir, exist_ok=True)
        
        # Copiar arquivos de dados
        if os.path.exists(DATA_FILE):
            shutil.copy2(DATA_FILE, os.path.join(backup_dir, 'motoristas.json'))
        
        # Copiar uploads
        if os.path.exists('uploads'):
            shutil.copytree('uploads', os.path.join(backup_dir, 'uploads'))
        
        # Criar arquivo ZIP
        shutil.make_archive(backup_name, 'zip', backup_dir)
        
        # Limpar diretório temporário
        shutil.rmtree(backup_dir)
        
        app.logger.info(f"Backup criado: {backup_path}")
        return backup_path
    except Exception as e:
        app.logger.error(f"Erro ao criar backup: {str(e)}")
        raise e
