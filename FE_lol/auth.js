// auth.js - Authentication module (UPDATED)
class AuthModule {
    constructor(app) {
        this.app = app;
        this.setupAuthForms();
    }

    setupAuthForms() {
        // Real-time form validation
        this.setupPhoneValidation();
        this.setupPasswordValidation();
    }

    setupPhoneValidation() {
        const phoneInputs = document.querySelectorAll('input[type="tel"]');
        phoneInputs.forEach(input => {
            input.addEventListener('blur', (e) => {
                this.validatePhoneNumber(e.target);
            });

            // Remove the formatting on input since it's causing API issues
            // Just store the raw numbers internally
            input.addEventListener('input', (e) => {
                this.storeRawPhoneNumber(e.target);
            });
        });
    }

    setupPasswordValidation() {
        const passwordInputs = document.querySelectorAll('input[type="password"]');
        passwordInputs.forEach(input => {
            input.addEventListener('blur', (e) => {
                this.validatePassword(e.target);
            });
        });
    }

    validatePhoneNumber(input) {
        const rawPhone = input.getAttribute('data-raw-phone') || input.value.replace(/\D/g, '');
        const errorElement = input.parentNode.querySelector('.error-message') || this.createErrorElement(input);

        if (!rawPhone) {
            this.showError(input, errorElement, 'Phone number is required');
            return false;
        }

        // Basic phone validation - require at least 10 digits
        if (rawPhone.length < 10) {
            this.showError(input, errorElement, 'Please enter a valid phone number (at least 10 digits)');
            return false;
        }

        // Format for display (but keep raw value for API calls)
        const formatted = this.formatPhoneForDisplay(rawPhone);
        input.value = formatted;
        input.setAttribute('data-raw-phone', rawPhone);

        this.clearError(input, errorElement);
        return true;
    }

    storeRawPhoneNumber(input) {
        const rawPhone = input.value.replace(/\D/g, '');
        input.setAttribute('data-raw-phone', rawPhone);
        
        // Update display with formatting
        if (rawPhone.length > 0) {
            const formatted = this.formatPhoneForDisplay(rawPhone);
            input.value = formatted;
        }
    }

    formatPhoneForDisplay(phone) {
        // Format for display only - backend gets raw numbers
        const cleaned = phone.replace(/\D/g, '');
        const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/);
        if (match) {
            return match[1] + ' ' + match[2] + ' ' + match[3];
        }
        return cleaned;
    }

    validatePassword(input) {
        const password = input.value;
        const errorElement = input.parentNode.querySelector('.error-message') || this.createErrorElement(input);

        if (!password) {
            this.showError(input, errorElement, 'Password is required');
            return false;
        }

        if (password.length < 6) {
            this.showError(input, errorElement, 'Password must be at least 6 characters');
            return false;
        }

        this.clearError(input, errorElement);
        return true;
    }

    createErrorElement(input) {
        const errorElement = document.createElement('div');
        errorElement.className = 'error-message';
        input.parentNode.appendChild(errorElement);
        return errorElement;
    }

    showError(input, errorElement, message) {
        input.classList.add('error');
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    }

    clearError(input, errorElement) {
        input.classList.remove('error');
        errorElement.style.display = 'none';
    }

    getRawPhoneNumber(input) {
        return input.getAttribute('data-raw-phone') || input.value.replace(/\D/g, '');
    }

    validateAuthForm(formType) {
        const form = document.getElementById(`${formType}Form`);
        const inputs = form.querySelectorAll('input[required]');
        let isValid = true;

        inputs.forEach(input => {
            if (input.type === 'tel') {
                if (!this.validatePhoneNumber(input)) isValid = false;
            } else if (input.type === 'password') {
                if (!this.validatePassword(input)) isValid = false;
            } else {
                if (!input.value.trim()) {
                    isValid = false;
                    const errorElement = input.parentNode.querySelector('.error-message') || this.createErrorElement(input);
                    this.showError(input, errorElement, 'This field is required');
                }
            }
        });

        return isValid;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.authModule = new AuthModule(window.app);
});