
document.addEventListener("DOMContentLoaded", function () {

    /* Helpers */
    function show(el) {
        el?.classList.remove("d-none");
    }

    function hide(el) {
        el?.classList.add("d-none");
    }

    /* === LEGAL TYPE === */
    const legalTypeField = document.getElementById("id_legal_type");
    const privateFields = document.getElementById("private-fields");
    const shopkeeperFields = document.getElementById("shopkeeper-fields");

    function toggleLegalTypeFields() {
        const selected = legalTypeField.value;

        if (selected === "PRIVATE") {
            show(privateFields);
            hide(shopkeeperFields);
        } 
        else if (selected === "SHOPKEEPER") {
            hide(privateFields);
            show(shopkeeperFields);
        } 
        else {
            hide(privateFields);
            hide(shopkeeperFields);
        }
    }

    legalTypeField.addEventListener("change", toggleLegalTypeFields);
    toggleLegalTypeFields();

    /* === ROLES === */
    const roleCheckboxes = document.querySelectorAll('input[name="role_types"]');
    const buyerFields = document.getElementById("buyer-fields");
    const sellerFields = document.getElementById("seller-fields");

    function toggleRoleFields() {
        let selectedRoles = Array.from(roleCheckboxes)
            .filter(cb => cb.checked)
            .map(cb => cb.value);

        selectedRoles.includes("BUYER") ? show(buyerFields) : hide(buyerFields);
        selectedRoles.includes("SELLER") ? show(sellerFields) : hide(sellerFields);
    }

    roleCheckboxes.forEach(cb => cb.addEventListener("change", toggleRoleFields));
    toggleRoleFields();
    
});