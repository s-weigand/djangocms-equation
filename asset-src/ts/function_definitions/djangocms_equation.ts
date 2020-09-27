import renderMathInElement, {
  RenderMathInElementOptions,
} from 'katex/dist/contrib/auto-render'

import 'katex/contrib/mhchem/mhchem'

export const debug_printer = (debug = true, ...args: any[]): void => {
  if (process.env.NODE_ENV === 'development' && debug) {
    // Or, `process.env.NODE_ENV !== 'production'`
    // Only runs in development and will be stripped from production build.
    console.log(...args)
  }
}

const katex_delimiters_setting: RenderMathInElementOptions = {
  delimiters: [
    { left: '$$', right: '$$', display: true },
    { left: '\\[', right: '\\]', display: true },
    { left: '$', right: '$', display: false },
    { left: '\\(', right: '\\)', display: false },
  ],
}

export const render_full_page = (target = document.body): void => {
  renderMathInElement(target, {
    ...katex_delimiters_setting,
  })
}

export const init_render_edit_mode = (debug = true): void => {
  debug_printer(debug, 'init_render_edit_mode did run')
  render_full_page()
  // window needs to be cast to any since the property 'CMS'
  // gets injected to windows by the javascript code of django-cms
  const CMS = (window as any).CMS
  if (CMS !== undefined) {
    CMS.$(window).on('cms-content-refresh', function () {
      render_full_page()
    })
  }

  debug_printer(debug, 'page loaded')
  let cms_btn: HTMLAnchorElement | null = document.querySelector(
    '.cms-toolbar-item-cms-mode-switcher a'
  )
  const render_structure_content_on_show = (): void => {
    let structure_content: HTMLDivElement | null = document.querySelector(
      '.cms-structure-content'
    ) as HTMLDivElement
    if (structure_content !== null) {
      // check if the element is visible
      if (structure_content.offsetParent !== null) {
        debug_printer(
          debug,
          'init_render_edit_mode\ncms_btn clicked => rendering all'
        )
        renderMathInElement(structure_content, {
          throwOnError: false,
          ...katex_delimiters_setting,
        })
      } else {
        debug_printer(debug, 'need delay')
        setTimeout(render_structure_content_on_show, 200)
      }
    }
  }
  debug_printer(debug, 'init_render_edit_mode\ncms_btn is:', cms_btn)
  if (cms_btn !== null) {
    // somehow onclick doesn't work, onfocus will be the hotfix for now
    cms_btn.onfocus = render_structure_content_on_show
  }
}
