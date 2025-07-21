// Funcionalidades gerais da aplicação

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips do Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Inicializar popovers do Bootstrap
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Configurar busca na página inicial
    setupSearch();
    
    // Auto-dismiss alerts
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            if (alert.classList.contains('alert-success')) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        });
    }, 5000);
    
    // Configurar validação de arquivos
    setupFileValidation();
});

function setupSearch() {
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    const searchResults = document.getElementById('searchResults');
    
    if (searchInput && searchBtn && searchResults) {
        searchBtn.addEventListener('click', performSearch);
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
    }
}

function performSearch() {
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');
    const query = searchInput.value.trim();
    
    if (!query) {
        searchResults.innerHTML = '';
        return;
    }
    
    // Mostrar loading
    searchResults.innerHTML = '<div class="text-center"><div class="loading"></div> Buscando...</div>';
    
    fetch(`/buscar?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            if (data.length === 0) {
                searchResults.innerHTML = '<p class="text-muted">Nenhum motorista encontrado.</p>';
            } else {
                let html = '<div class="list-group">';
                data.forEach(motorista => {
                    html += `
                        <a href="/motorista/${motorista.id}" class="list-group-item list-group-item-action">
                            <div class="d-flex w-100 justify-content-between">
                                <h6 class="mb-1">${motorista.nome}</h6>
                                <small>${motorista.cpf}</small>
                            </div>
                            <small class="text-muted">${motorista.celular}</small>
                        </a>
                    `;
                });
                html += '</div>';
                searchResults.innerHTML = html;
            }
        })
        .catch(error => {
            console.error('Erro na busca:', error);
            searchResults.innerHTML = '<p class="text-danger">Erro ao realizar busca.</p>';
        });
}

function setupFileValidation() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Validar tamanho do arquivo (máximo 16MB)
                if (file.size > 16 * 1024 * 1024) {
                    alert('Arquivo muito grande. Tamanho máximo permitido: 16MB');
                    e.target.value = '';
                    return;
                }
                
                // Validar tipo de arquivo
                const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'application/pdf'];
                if (!allowedTypes.includes(file.type)) {
                    alert('Tipo de arquivo não permitido. Apenas imagens (JPG, PNG, GIF) e PDF são aceitos.');
                    e.target.value = '';
                    return;
                }
                
                // Mostrar preview para imagens
                if (file.type.startsWith('image/')) {
                    showImagePreview(input, file);
                }
            }
        });
    });
}

function showImagePreview(input, file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        const inputId = input.id;
        let preview = document.getElementById(inputId + '-preview');
        
        if (!preview) {
            preview = input.parentNode.querySelector('.image-preview');
            if (!preview) {
                preview = document.createElement('div');
                preview.className = 'image-preview mt-2';
                preview.id = inputId + '-preview';
                input.parentNode.appendChild(preview);
            }
        }
        
        preview.innerHTML = `
            <div class="d-flex align-items-center">
                <img src="${e.target.result}" class="img-thumbnail me-3" style="max-width: 150px; max-height: 150px;">
                <div>
                    <p class="mb-1"><strong>Arquivo:</strong> ${file.name}</p>
                    <p class="mb-1"><strong>Tamanho:</strong> ${(file.size / 1024 / 1024).toFixed(2)} MB</p>
                    <button type="button" class="btn btn-sm btn-danger" onclick="removePreview(this, '${inputId}')">
                        <i class="fas fa-times"></i> Remover
                    </button>
                </div>
            </div>
        `;
    };
    reader.readAsDataURL(file);
}

function removePreview(button, inputId) {
    const preview = button.closest('.image-preview');
    const input = document.getElementById(inputId);
    if (input) {
        input.value = '';
    }
    if (preview) {
        preview.remove();
    }
}

// Função para mostrar/ocultar loading
function showLoading(element) {
    element.innerHTML = '<div class="loading"></div> Carregando...';
}

function hideLoading(element) {
    element.innerHTML = '';
}

// Função para confirmar ações
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Função para formatar data
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
}

// Função para calcular idade
function calculateAge(birthDate) {
    const today = new Date();
    const birth = new Date(birthDate);
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
        age--;
    }
    
    return age;
}

// Função para verificar se documento está próximo do vencimento
function isDocumentExpiring(validityDate, daysWarning = 30) {
    const today = new Date();
    const validity = new Date(validityDate);
    const diffTime = validity - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    return diffDays <= daysWarning && diffDays > 0;
}

// Função para verificar se documento está vencido
function isDocumentExpired(validityDate) {
    const today = new Date();
    const validity = new Date(validityDate);
    return validity < today;
}

// Função para exibir notificações
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remover após 5 segundos
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

// Função para copiar texto para clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Texto copiado para a área de transferência!', 'success');
    }).catch(err => {
        console.error('Erro ao copiar texto:', err);
        showNotification('Erro ao copiar texto', 'danger');
    });
}

// Função para download de arquivo
function downloadFile(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Função para imprimir página
function printPage() {
    window.print();
}

// Função para voltar ao topo da página
function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Adicionar botão de voltar ao topo se a página for longa
window.addEventListener('scroll', function() {
    let scrollBtn = document.getElementById('scrollToTopBtn');
    
    if (window.pageYOffset > 300) {
        if (!scrollBtn) {
            scrollBtn = document.createElement('button');
            scrollBtn.id = 'scrollToTopBtn';
            scrollBtn.className = 'btn btn-primary position-fixed';
            scrollBtn.style.bottom = '20px';
            scrollBtn.style.right = '20px';
            scrollBtn.style.zIndex = '9999';
            scrollBtn.style.borderRadius = '50%';
            scrollBtn.style.width = '50px';
            scrollBtn.style.height = '50px';
            scrollBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
            scrollBtn.onclick = scrollToTop;
            document.body.appendChild(scrollBtn);
        }
        scrollBtn.style.display = 'block';
    } else {
        if (scrollBtn) {
            scrollBtn.style.display = 'none';
        }
    }
});
