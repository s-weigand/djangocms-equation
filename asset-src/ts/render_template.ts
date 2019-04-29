import { render } from 'katex'
import {
  init_render_main_page,
  debug_printer,
  render_full_page,
} from './djangocms_equation'

init_render_main_page(true)

// just for debugging
document.addEventListener('DOMContentLoaded', function(event) {
  const find_elements = (iframe1: HTMLIFrameElement) => {
    debug_printer(true, ' running find_elements')
    // let iframe1: HTMLIFrameElement | null = document.querySelector(
    //   'iframe'
    // ) as HTMLIFrameElement
    if (
      iframe1 !== null &&
      iframe1.contentDocument !== null &&
      iframe1.contentDocument.readyState === 'complete'
    ) {
      let iframe2: HTMLIFrameElement | null = iframe1.contentDocument.querySelector(
        'iframe.cke_wysiwyg_frame'
      ) as HTMLIFrameElement
      if (
        iframe2 !== null &&
        iframe2.contentDocument !== null &&
        iframe2.contentDocument.readyState === 'complete'
      ) {
        const katex_spans:
          | NodeListOf<HTMLSpanElement>
          | [] = iframe2.contentDocument.querySelectorAll(
          'cms-plugin span.katex'
        )
        if (katex_spans.length !== 0) {
          let CKeditorBodyTag = iframe2.contentDocument.querySelector(
            'body'
          ) as HTMLBodyElement
          render_full_page(CKeditorBodyTag)
        }
        debug_printer(
          true,
          'cms-plugin span.katex',
          iframe2.contentDocument.querySelectorAll('cms-plugin span.katex')
        )
      } else {
        debug_printer(true, 'iframe2 was null or content was null')
        setTimeout(() => find_elements(iframe1), 500)
      }
    } else {
      debug_printer(true, 'iframe1 was null or content was null')
      setTimeout(() => find_elements(iframe1), 500)
    }
  }
  // original from:
  // https://stackoverflow.com/a/49023264/3990615
  function callback(records: any) {
    records.forEach(function(record: any) {
      let list = record.addedNodes
      let i = list.length - 1

      for (; i > -1; i--) {
        if (list[i].nodeName === 'IFRAME') {
          // Insert code here...
          console.log(list[i])
          find_elements(list[i])
        }
      }
    })
  }

  let observer = new MutationObserver(callback)

  let targetNode = document.body

  observer.observe(targetNode, { childList: true, subtree: true })
})
