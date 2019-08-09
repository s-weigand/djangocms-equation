import { init_render_edit_mode } from './function_definitions/djangocms_equation'

import { init_ckeditor_rendering } from './function_definitions/ckeditor_rendner'

if (document.readyState === 'complete') {
  init_render_edit_mode(false)
  init_ckeditor_rendering(true)
} else {
  document.addEventListener('DOMContentLoaded', function(event) {
    init_render_edit_mode(false)
    init_ckeditor_rendering(true)
  })
}
