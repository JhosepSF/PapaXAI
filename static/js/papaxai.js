/**
 * PapaXAI — Lógica de Interfaz de Usuario Vanilla JavaScript
 * Gestiona el arrastre y suelta, vista previa de imágenes foliares,
 * selección de muestras de prueba y la retroalimentación visual del pipeline.
 */

document.addEventListener('DOMContentLoaded', () => {
  initDropzone();
  initSampleSelector();
  initFormSubmission();
});

/**
 * Inicializa la zona interactiva de carga (Drag and Drop)
 */
function initDropzone() {
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('file-input');
  const previewContainer = document.getElementById('preview-container');
  const previewImg = document.getElementById('preview-img');
  const previewFilename = document.getElementById('preview-filename');
  const previewFilesize = document.getElementById('preview-filesize');
  const removeBtn = document.getElementById('btn-remove-image');
  const analyzeBtn = document.getElementById('btn-analyze');
  const hiddenSampleInput = document.getElementById('muestra-seleccionada-input');

  if (!dropzone || !fileInput) return;

  // Clic en la zona abre el explorador
  dropzone.addEventListener('click', (e) => {
    if (e.target !== removeBtn) {
      fileInput.click();
    }
  });

  // Eventos de arrastre
  ['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.add('dragover');
    });
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.remove('dragover');
    });
  });

  // Soltar archivo
  dropzone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files && files.length > 0) {
      handleFileSelected(files[0]);
    }
  });

  // Cambio en el input de archivo
  fileInput.addEventListener('change', () => {
    if (fileInput.files && fileInput.files.length > 0) {
      handleFileSelected(fileInput.files[0]);
    }
  });

  // Eliminar selección
  if (removeBtn) {
    removeBtn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      clearSelection();
    });
  }

  function handleFileSelected(file) {
    // Validar tipo de archivo
    const validExtensions = ['jpg', 'jpeg', 'png', 'webp'];
    const ext = file.name.split('.').pop().toLowerCase();
    
    if (!validExtensions.includes(ext)) {
      alert(`El formato .${ext} no es admitido. Seleccione una imagen en formato JPG, PNG o WEBP.`);
      return;
    }

    // Validar tamaño (máximo 10MB)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
      alert(`La imagen pesa ${(file.size / (1024 * 1024)).toFixed(1)} MB. El límite máximo admitido es 10 MB.`);
      return;
    }

    // Desactivar cualquier muestra previa de prueba
    if (hiddenSampleInput) hiddenSampleInput.value = '';
    document.querySelectorAll('.sample-card').forEach(c => c.classList.remove('active'));

    // Mostrar vista previa
    const reader = new FileReader();
    reader.onload = (e) => {
      previewImg.src = e.target.result;
      previewFilename.textContent = file.name;
      const sizeKB = (file.size / 1024).toFixed(1);
      previewFilesize.textContent = `${sizeKB} KB (${file.type || 'imagen'})`;
      
      dropzone.style.display = 'none';
      previewContainer.style.display = 'block';
      if (analyzeBtn) {
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = 'Analizar fotografía foliar';
      }
    };
    reader.readAsDataURL(file);
  }

  function clearSelection() {
    fileInput.value = '';
    if (hiddenSampleInput) hiddenSampleInput.value = '';
    previewImg.src = '';
    previewContainer.style.display = 'none';
    dropzone.style.display = 'block';
    document.querySelectorAll('.sample-card').forEach(c => c.classList.remove('active'));
    if (analyzeBtn) {
      analyzeBtn.disabled = true;
      analyzeBtn.textContent = 'Seleccione una imagen para analizar';
    }
  }

  // Exponer a ventana para el selector de muestras
  window.papaXAI_clear = clearSelection;
}

/**
 * Inicializa la selección rápida de imágenes de prueba para evaluadores
 */
function initSampleSelector() {
  const sampleCards = document.querySelectorAll('.sample-card');
  const hiddenSampleInput = document.getElementById('muestra-seleccionada-input');
  const fileInput = document.getElementById('file-input');
  const dropzone = document.getElementById('dropzone');
  const previewContainer = document.getElementById('preview-container');
  const previewImg = document.getElementById('preview-img');
  const previewFilename = document.getElementById('preview-filename');
  const previewFilesize = document.getElementById('preview-filesize');
  const analyzeBtn = document.getElementById('btn-analyze');

  sampleCards.forEach(card => {
    card.addEventListener('click', () => {
      const filename = card.getAttribute('data-filename');
      const imgSrc = card.querySelector('img').src;
      const label = card.getAttribute('data-label') || filename;

      sampleCards.forEach(c => c.classList.remove('active'));
      card.classList.add('active');

      if (fileInput) fileInput.value = '';
      if (hiddenSampleInput) hiddenSampleInput.value = filename;

      // Mostrar en preview
      previewImg.src = imgSrc;
      previewFilename.textContent = filename;
      previewFilesize.textContent = `Muestra del conjunto de prueba [Etiqueta esperada: ${label}]`;
      
      if (dropzone) dropzone.style.display = 'none';
      if (previewContainer) previewContainer.style.display = 'block';
      if (analyzeBtn) {
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = `Analizar muestra (${filename})`;
      }
    });
  });
}

/**
 * Gestiona el envío del formulario y la simulación de fases de procesamiento real
 */
function initFormSubmission() {
  const form = document.getElementById('analysis-form');
  const overlay = document.getElementById('progress-overlay');
  const step1 = document.getElementById('step-validate');
  const step2 = document.getElementById('step-resnet');
  const step3 = document.getElementById('step-xgboost');
  const step4 = document.getElementById('step-xai');

  if (!form || !overlay) return;

  form.addEventListener('submit', () => {
    overlay.style.display = 'flex';

    // Fases visuales sincrónicas con el procesamiento del backend
    setTimeout(() => {
      if (step1) {
        step1.classList.remove('active');
        step1.classList.add('done');
      }
      if (step2) step2.classList.add('active');
    }, 600);

    setTimeout(() => {
      if (step2) {
        step2.classList.remove('active');
        step2.classList.add('done');
      }
      if (step3) step3.classList.add('active');
    }, 1800);

    setTimeout(() => {
      if (step3) {
        step3.classList.remove('active');
        step3.classList.add('done');
      }
      if (step4) step4.classList.add('active');
    }, 2400);
  });
}
