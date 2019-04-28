import { init_render_main_page, debug_printer } from './djangocms_equation'

init_render_main_page(true)

// just for debugging
document.addEventListener('DOMContentLoaded', function(event) {
  const find_elements = () => {
    debug_printer(true, ' running find_elements')
    let cms_plugins = document.querySelectorAll('cms-plugin')
    if (cms_plugins.length !== 0) {
      debug_printer(true, 'body', document.querySelector('body'))
      debug_printer(true, 'cms-plugin', cms_plugins)
      debug_printer(
        true,
        'cms-plugin span.katex',
        document.querySelectorAll('cms-plugin span.katex')
      )
      setTimeout(find_elements, 10000)
    }
  }
  find_elements()
})
