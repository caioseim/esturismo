// Validações e máscaras para formulários

function applyCpfMask() {
    const cpfInput = document.getElementById('cpf');
    if (cpfInput) {
        cpfInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            value = value.replace(/(\d{3})(\d)/, '$1.$2');
            value = value.replace(/(\d{3})(\d)/, '$1.$2');
            value = value.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
            e.target.value = value;
            
            // Validar CPF
            if (value.length === 14) {
                if (validateCpf(value)) {
                    cpfInput.classList.remove('is-invalid');
                    cpfInput.classList.add('is-valid');
                } else {
                    cpfInput.classList.remove('is-valid');
                    cpfInput.classList.add('is-invalid');
                }
            } else {
                cpfInput.classList.remove('is-valid', 'is-invalid');
            }
        });
    }
}

function applyPhoneMask() {
    const phoneInput = document.getElementById('celular');
    if (phoneInput) {
        phoneInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            
            if (value.length <= 10) {
                value = value.replace(/(\d{2})(\d)/, '($1) $2');
                value = value.replace(/(\d{4})(\d)/, '$1-$2');
            } else {
                value = value.replace(/(\d{2})(\d)/, '($1) $2');
                value = value.replace(/(\d{5})(\d)/, '$1-$2');
            }
            
            e.target.value = value;
        });
    }
}

function validateCpf(cpf) {
    cpf = cpf.replace(/\D/g, '');
    
    if (cpf.length !== 11 || /^(\d)\1{10}$/.test(cpf)) {
        return false;
    }
    
    let sum = 0;
    for (let i = 0; i < 9; i++) {
        sum += parseInt(cpf.charAt(i)) * (10 - i);
    }
    
    let remainder = sum % 11;
    let digit1 = remainder < 2 ? 0 : 11 - remainder;
    
    if (parseInt(cpf.charAt(9)) !== digit1) {
        return false;
    }
    
    sum = 0;
    for (let i = 0; i < 10; i++) {
        sum += parseInt(cpf.charAt(i)) * (11 - i);
    }
    
    remainder = sum % 11;
    let digit2 = remainder < 2 ? 0 : 11 - remainder;
    
    return parseInt(cpf.charAt(10)) === digit2;
}

function validateForm() {
    const form = document.getElementById('cadastroForm');
    if (!form) return true;
    
    const cpfInput = document.getElementById('cpf');
    const nomeInput = document.getElementById('nome');
    const celularInput = document.getElementById('celular');
    
    let isValid = true;
    
    // Validar nome
    if (nomeInput.value.trim().length < 2) {
        showFieldError(nomeInput, 'Nome deve ter pelo menos 2 caracteres');
        isValid = false;
    } else {
        clearFieldError(nomeInput);
    }
    
    // Validar CPF
    if (!validateCpf(cpfInput.value)) {
        showFieldError(cpfInput, 'CPF inválido');
        isValid = false;
    } else {
        clearFieldError(cpfInput);
    }
    
    // Validar celular
    const phoneRegex = /^\(\d{2}\) \d{4,5}-\d{4}$/;
    if (!phoneRegex.test(celularInput.value)) {
        showFieldError(celularInput, 'Número de celular inválido');
        isValid = false;
    } else {
        clearFieldError(celularInput);
    }
    
    return isValid;
}

function showFieldError(field, message) {
    field.classList.add('is-invalid');
    field.classList.remove('is-valid');
    
    let feedback = field.nextElementSibling;
    if (!feedback || !feedback.classList.contains('invalid-feedback')) {
        feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        field.parentNode.appendChild(feedback);
    }
    feedback.textContent = message;
}

function clearFieldError(field) {
    field.classList.remove('is-invalid');
    field.classList.add('is-valid');
    
    const feedback = field.nextElementSibling;
    if (feedback && feedback.classList.contains('invalid-feedback')) {
        feedback.remove();
    }
}

// Validar formulário antes do envio
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('cadastroForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            if (!validateForm()) {
                e.preventDefault();
                alert('Por favor, corrija os erros no formulário antes de continuar.');
            }
        });
    }
});
