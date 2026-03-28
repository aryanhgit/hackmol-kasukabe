document.addEventListener('DOMContentLoaded', () => {
  const addRowButton = document.querySelector('[data-add-row]');
  const container = document.querySelector('[data-formset-container]');
  const template = document.getElementById('medicine-empty-form-template');
  const totalForms = document.getElementById('id_medicines-TOTAL_FORMS');

  if (!addRowButton || !container || !template || !totalForms) {
    return;
  }

  addRowButton.addEventListener('click', () => {
    const formIndex = Number(totalForms.value);
    const newMarkup = template.innerHTML.replaceAll('__prefix__', String(formIndex));
    container.insertAdjacentHTML('beforeend', newMarkup);
    totalForms.value = String(formIndex + 1);
  });
});
