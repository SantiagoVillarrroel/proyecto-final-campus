// Validaciones mínimas del lado del cliente. La validación real está en
// app/schemas.py: esto solo mejora la experiencia de uso.

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("form[data-confirmar]").forEach((formulario) => {
    formulario.addEventListener("submit", (evento) => {
      const mensaje = formulario.dataset.confirmar || "¿Confirmar esta acción?";
      if (!window.confirm(mensaje)) {
        evento.preventDefault();
      }
    });
  });

  document.querySelectorAll("form[data-validar]").forEach((formulario) => {
    formulario.addEventListener("submit", (evento) => {
      const nombre = formulario.elements["nombre"];
      const sku = formulario.elements["sku"];

      if (!nombre.value.trim()) {
        evento.preventDefault();
        nombre.focus();
        return;
      }

      if (!sku.value.trim()) {
        evento.preventDefault();
        sku.focus();
      }
    });
  });
});
