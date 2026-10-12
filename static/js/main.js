/**
 * INVENTRA - Frontend Interactive Logic
 * Handles modal pre-population, live table search/filtering, and stock adjustments
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Initialize Bootstrap Tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // 2. Auto-dismiss flash alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            try {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                bsAlert.close();
            } catch (e) {
                // Ignore if already closed
            }
        }, 5000);
    });

    // 3. Live Table Search & Filter (client-side instant filtering)
    const tableSearchInput = document.getElementById('tableSearchInput');
    if (tableSearchInput) {
        tableSearchInput.addEventListener('input', function () {
            const filter = this.value.toLowerCase();
            const targetTable = document.querySelector('.searchable-table tbody');
            if (!targetTable) return;

            const rows = targetTable.querySelectorAll('tr');
            rows.forEach(function (row) {
                const text = row.textContent.toLowerCase();
                if (text.includes(filter)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }

    // 4. Pre-populate Edit Product Modal
    const editProductModal = document.getElementById('editProductModal');
    if (editProductModal) {
        editProductModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            if (!button) return;

            const id = button.getAttribute('data-id');
            const name = button.getAttribute('data-name');
            const sku = button.getAttribute('data-sku') || '';
            const category = button.getAttribute('data-category') || '';
            const quantity = button.getAttribute('data-quantity');
            const price = button.getAttribute('data-price');
            const minStock = button.getAttribute('data-min-stock') || '10';
            const supplierId = button.getAttribute('data-supplier-id');

            // Populate form fields
            const inputId = editProductModal.querySelector('input[name="id"]');
            const inputName = editProductModal.querySelector('input[name="name"]');
            const inputSku = editProductModal.querySelector('input[name="sku"]');
            const inputCategory = editProductModal.querySelector('input[name="category"]');
            const inputQuantity = editProductModal.querySelector('input[name="quantity"]');
            const inputPrice = editProductModal.querySelector('input[name="price"]');
            const inputMinStock = editProductModal.querySelector('input[name="min_stock"]');
            const selectSupplier = editProductModal.querySelector('select[name="supplier_id"]');

            if (inputId) inputId.value = id || '';
            if (inputName) inputName.value = name || '';
            if (inputSku) inputSku.value = sku;
            if (inputCategory) inputCategory.value = category;
            if (inputQuantity) inputQuantity.value = quantity || '';
            if (inputPrice) inputPrice.value = price || '';
            if (inputMinStock) inputMinStock.value = minStock;
            if (selectSupplier && supplierId) selectSupplier.value = supplierId;
        });
    }

    // 5. Pre-populate Delete Product Modal
    const deleteProductModal = document.getElementById('deleteProductModal');
    if (deleteProductModal) {
        deleteProductModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            if (!button) return;

            const id = button.getAttribute('data-id');
            const name = button.getAttribute('data-name');

            const inputId = deleteProductModal.querySelector('input[name="id"]');
            const nameSpan = deleteProductModal.querySelector('#deleteProductName');

            if (inputId) inputId.value = id || '';
            if (nameSpan) nameSpan.textContent = name || ('ID #' + id);
        });
    }

    // 6. Pre-populate Edit Supplier Modal
    const editSupplierModal = document.getElementById('editSupplierModal');
    if (editSupplierModal) {
        editSupplierModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            if (!button) return;

            const id = button.getAttribute('data-id');
            const company = button.getAttribute('data-company');
            const person = button.getAttribute('data-person');
            const phone = button.getAttribute('data-phone');
            const email = button.getAttribute('data-email');
            const address = button.getAttribute('data-address');

            const inputId = editSupplierModal.querySelector('input[name="id"]');
            const inputCompany = editSupplierModal.querySelector('input[name="company_name"]');
            const inputPerson = editSupplierModal.querySelector('input[name="contact_person"]');
            const inputPhone = editSupplierModal.querySelector('input[name="phone"]');
            const inputEmail = editSupplierModal.querySelector('input[name="email"]');
            const inputAddress = editSupplierModal.querySelector('textarea[name="address"]') || editSupplierModal.querySelector('input[name="address"]');

            if (inputId) inputId.value = id || '';
            if (inputCompany) inputCompany.value = company || '';
            if (inputPerson) inputPerson.value = person || '';
            if (inputPhone) inputPhone.value = phone || '';
            if (inputEmail) inputEmail.value = email || '';
            if (inputAddress) inputAddress.value = address || '';
        });
    }

    // 7. Pre-populate Delete Supplier Modal
    const deleteSupplierModal = document.getElementById('deleteSupplierModal');
    if (deleteSupplierModal) {
        deleteSupplierModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            if (!button) return;

            const id = button.getAttribute('data-id');
            const company = button.getAttribute('data-company');
            const count = button.getAttribute('data-count') || '0';

            const inputId = deleteSupplierModal.querySelector('input[name="id"]');
            const companySpan = deleteSupplierModal.querySelector('#deleteSupplierName');
            const countWarning = deleteSupplierModal.querySelector('#deleteSupplierCountWarning');

            if (inputId) inputId.value = id || '';
            if (companySpan) companySpan.textContent = company || ('ID #' + id);
            if (countWarning) {
                if (parseInt(count) > 0) {
                    countWarning.textContent = `Warning: This supplier currently has ${count} associated product(s). Deleting will also remove or unlink these products.`;
                    countWarning.classList.remove('d-none');
                } else {
                    countWarning.classList.add('d-none');
                }
            }
        });
    }

    // 8. Quick Stock Adjustment Modal
    const adjustStockModal = document.getElementById('adjustStockModal');
    if (adjustStockModal) {
        adjustStockModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            if (!button) return;

            const id = button.getAttribute('data-id');
            const name = button.getAttribute('data-name');
            const currentQty = button.getAttribute('data-quantity');

            const inputId = adjustStockModal.querySelector('input[name="id"]');
            const nameSpan = adjustStockModal.querySelector('#adjustProductName');
            const qtySpan = adjustStockModal.querySelector('#adjustCurrentQty');

            if (inputId) inputId.value = id;
            if (nameSpan) nameSpan.textContent = name;
            if (qtySpan) qtySpan.textContent = currentQty;
        });
    }
});
