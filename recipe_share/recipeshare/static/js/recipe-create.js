(() => {
  const CHEF_HAT_SVG = `
    <span class="recipe-preview-chef-icon" data-preview-placeholder-icon aria-hidden="true">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
        <path d="M6 13.87A4 4 0 0 1 7.41 6a5.11 5.11 0 0 1 1.05-1.54 5 5 0 0 1 7.08 0A5.11 5.11 0 0 1 16.59 6 4 4 0 0 1 18 13.87V21H6Z"/>
        <line x1="6" y1="17" x2="18" y2="17"/>
      </svg>
    </span>
  `;

  const isVideoFile = (file) => {
    if (!file) return false;
    if (file.type && file.type.startsWith('video/')) return true;
    return /\.(mp4|webm|mov|ogg|ogv|m4v)$/i.test(file.name || '');
  };

  const initializeRecipeCreate = (root = document) => {
    root.querySelectorAll('[data-recipe-create]').forEach(page => {
      if (page.dataset.initialized === 'true') return;
      page.dataset.initialized = 'true';

      const title = page.querySelector('[data-recipe-title]');
      const description = page.querySelector('[data-recipe-description]');
      const instructions = page.querySelector('[data-recipe-instructions]');
      const descCounter = page.querySelector('[data-desc-counter]');
      const instCounter = page.querySelector('[data-inst-counter]');
      const categorySelect = page.querySelector('[data-recipe-category-select]');
      const previewCategory = page.querySelector('[data-preview-category]');

      const imageInput = page.querySelector('#recipe_image');
      const videoInput = page.querySelector('#recipe_video');
      const dropzone = page.querySelector('[data-recipe-dropzone]');
      const previewImage = page.querySelector('[data-recipe-image-preview]');
      const previewVideo = page.querySelector('[data-recipe-video-preview]');
      const previewPlaceholder = page.querySelector('[data-recipe-upload-placeholder]');
      const previewCard = page.querySelector('[data-preview-image]');
      const statusInput = page.querySelector('[data-recipe-status-input]');
      const uploadClearBtn = page.querySelector('[data-recipe-upload-clear]');

      const defaultAccept = 'image/png,image/jpeg,image/webp,image/gif,video/mp4,video/webm,video/quicktime,video/ogg';
      let currentObjectUrl = null;

      const syncPreview = () => {
        const previewTitle = page.querySelector('[data-preview-title]');
        const previewDesc = page.querySelector('[data-preview-description]');
        if (previewTitle && title) {
          previewTitle.textContent = title.value.trim() || 'Your recipe title';
        }
        if (previewDesc && description) {
          previewDesc.textContent = description.value.trim() || 'Your description will appear here.';
        }
        if (descCounter && description) {
          descCounter.textContent = `${description.value.length}/200`;
        }
        if (instCounter && instructions) {
          instCounter.textContent = `${instructions.value.length}/500`;
        }
        if (previewCategory && categorySelect) {
          const selectedOpt = categorySelect.options[categorySelect.selectedIndex];
          const label = (selectedOpt && selectedOpt.value) ? selectedOpt.textContent.trim() : 'Your category';
          previewCategory.textContent = label;
        }
      };

      const renderMediaPreview = (file) => {
        if (!file) return;
        if (currentObjectUrl) {
          URL.revokeObjectURL(currentObjectUrl);
        }
        const url = URL.createObjectURL(file);
        currentObjectUrl = url;

        if (previewPlaceholder) previewPlaceholder.hidden = true;
        if (uploadClearBtn) uploadClearBtn.hidden = false;

        if (isVideoFile(file)) {
          if (previewImage) {
            previewImage.hidden = true;
            previewImage.removeAttribute('src');
          }
          if (previewVideo) {
            previewVideo.src = url;
            previewVideo.hidden = false;
          }
          if (previewCard) {
            previewCard.style.backgroundImage = '';
            previewCard.innerHTML = `<video src="${url}" muted loop autoplay playsinline preload="metadata"></video>`;
          }
        } else {
          if (previewVideo) {
            previewVideo.pause();
            previewVideo.removeAttribute('src');
            previewVideo.hidden = true;
          }
          if (previewImage) {
            previewImage.src = url;
            previewImage.hidden = false;
          }
          if (previewCard) {
            previewCard.style.backgroundImage = '';
            previewCard.innerHTML = `<img src="${url}" alt="Recipe preview">`;
          }
        }
      };

      const clearMediaPreview = () => {
        if (currentObjectUrl) {
          URL.revokeObjectURL(currentObjectUrl);
          currentObjectUrl = null;
        }
        if (imageInput) imageInput.value = '';
        if (videoInput) videoInput.value = '';
        if (previewVideo) {
          previewVideo.pause();
          previewVideo.removeAttribute('src');
          previewVideo.hidden = true;
        }
        if (previewImage) {
          previewImage.removeAttribute('src');
          previewImage.hidden = true;
        }
        if (previewPlaceholder) {
          previewPlaceholder.hidden = false;
        }
        if (uploadClearBtn) {
          uploadClearBtn.hidden = true;
        }
        if (previewCard) {
          previewCard.style.backgroundImage = '';
          previewCard.innerHTML = CHEF_HAT_SVG;
        }
      };

      title?.addEventListener('input', syncPreview);
      description?.addEventListener('input', syncPreview);
      instructions?.addEventListener('input', syncPreview);
      categorySelect?.addEventListener('change', syncPreview);

      previewVideo?.addEventListener('click', (event) => {
        event.stopPropagation();
      });

      imageInput?.addEventListener('change', () => {
        const file = imageInput.files?.[0];
        if (!file) return;
        if (videoInput) videoInput.value = '';
        renderMediaPreview(file);
        imageInput.accept = defaultAccept;
      });

      videoInput?.addEventListener('change', () => {
        const file = videoInput.files?.[0];
        if (!file) return;
        if (imageInput) imageInput.value = '';
        renderMediaPreview(file);
      });

      uploadClearBtn?.addEventListener('click', (event) => {
        event.preventDefault();
        event.stopPropagation();
        clearMediaPreview();
      });

      if (dropzone && imageInput) {
        dropzone.addEventListener('dragover', (event) => {
          event.preventDefault();
          dropzone.classList.add('is-dragover');
        });
        dropzone.addEventListener('dragleave', () => {
          dropzone.classList.remove('is-dragover');
        });
        dropzone.addEventListener('drop', (event) => {
          event.preventDefault();
          dropzone.classList.remove('is-dragover');
          const file = event.dataTransfer?.files?.[0];
          if (!file) return;
          try {
            const dt = new DataTransfer();
            dt.items.add(file);
            if (isVideoFile(file) && videoInput) {
              videoInput.files = dt.files;
              imageInput.value = '';
            } else {
              imageInput.files = dt.files;
              if (videoInput) videoInput.value = '';
            }
          } catch (_) {
            // DataTransfer fallback
          }
          renderMediaPreview(file);
        });
      }

      page.querySelector('[data-add-ingredient]')?.addEventListener('click', () => {
        const row = document.createElement('div');
        row.className = 'ingredient-row';
        row.innerHTML = `
          <input name="ingredient_name" required placeholder="Ingredient name" aria-label="Ingredient">
          <input name="ingredient_quantity" required placeholder="Amount (e.g. 1 cup, 2 tbsp)" aria-label="Quantity">
          <select name="ingredient_unit" aria-label="Unit">
            <option value="">Unit</option>
            <option value="cup">cup</option>
            <option value="cups">cups</option>
            <option value="tbsp">tbsp</option>
            <option value="tsp">tsp</option>
            <option value="g">g</option>
            <option value="kg">kg</option>
            <option value="ml">ml</option>
            <option value="l">L</option>
            <option value="oz">oz</option>
            <option value="lb">lb</option>
            <option value="piece">piece</option>
            <option value="pieces">pieces</option>
            <option value="clove">clove</option>
            <option value="pinch">pinch</option>
            <option value="slice">slice</option>
          </select>
          <button type="button" class="ingredient-remove" data-remove-ingredient aria-label="Remove ingredient" title="Remove ingredient">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
          </button>
        `;
        page.querySelector('[data-ingredient-list]')?.append(row);
      });

      page.querySelector('[data-ingredient-list]')?.addEventListener('click', event => {
        if (!event.target.closest('[data-remove-ingredient]')) return;
        const rows = page.querySelectorAll('.ingredient-row');
        if (rows.length > 1) event.target.closest('.ingredient-row').remove();
      });

      page.querySelector('[data-save-draft]')?.addEventListener('click', () => {
        if (statusInput) statusInput.value = 'draft';
      });
      page.querySelector('[data-publish]')?.addEventListener('click', () => {
        if (statusInput) statusInput.value = 'published';
      });
    });
  };

  document.addEventListener('DOMContentLoaded', () => initializeRecipeCreate());
  document.addEventListener('recipe-share:page-loaded', () => initializeRecipeCreate(document));
})();
