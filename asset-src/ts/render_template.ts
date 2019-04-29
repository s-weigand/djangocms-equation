import {
  init_render_main_page,
  debug_printer,
  render_full_page,
} from './djangocms_equation'

init_render_main_page(true)

// just for debugging
document.addEventListener('DOMContentLoaded', function(event) {
  const iframe_is_loaded = (iframe: HTMLIFrameElement | null) => {
    if (
      iframe !== null &&
      iframe.contentDocument !== null &&
      iframe.contentDocument.readyState === 'complete'
    ) {
      return true
    } else {
      return false
    }
  }

  const CKEditor_render_equation_normal = (
    RootIFrame: HTMLIFrameElement,
    max_runs: number
  ) => {
    const RootIFrameDocument = RootIFrame.contentDocument as HTMLDocument
    let EditorIFrame: HTMLIFrameElement | null = RootIFrameDocument.querySelector(
      'iframe.cke_wysiwyg_frame'
    ) as HTMLIFrameElement
    if (iframe_is_loaded(EditorIFrame)) {
      const EditorIFrameDocument = EditorIFrame.contentDocument as HTMLDocument
      const katex_spans:
        | NodeListOf<HTMLSpanElement>
        | [] = EditorIFrameDocument.querySelectorAll('cms-plugin span.katex')
      if (katex_spans.length !== 0) {
        let TextPluginBodyTag = EditorIFrameDocument.querySelector(
          'body'
        ) as HTMLBodyElement
        render_full_page(TextPluginBodyTag)
      }
      debug_printer(
        true,
        'cms-plugin span.katex',
        EditorIFrameDocument.querySelectorAll('cms-plugin span.katex')
      )
    } else {
      if (max_runs >= 0) {
        debug_printer(
          true,
          'max_runs=',
          max_runs,
          '\nEditorIFrame was null or content was null',
          EditorIFrame
        )
        setTimeout(
          () => CKEditor_render_equation(RootIFrame, max_runs - 1),
          500
        )
      }
    }
  }

  const CKEditor_bind_rerender = (
    RootIFrame: HTMLIFrameElement,
    max_runs: number
  ) => {
    const RootIFrameDocument = RootIFrame.contentDocument as HTMLDocument
    let CKEditorDialogIFrame: HTMLIFrameElement | null = RootIFrameDocument.querySelector(
      '.cms-ckeditor-dialog iframe.cke_dialog_ui_html'
    ) as HTMLIFrameElement
    if (iframe_is_loaded(CKEditorDialogIFrame)) {
      const CKEditorDialogIFrameDocument = CKEditorDialogIFrame.contentDocument as HTMLDocument
      const EquationEditDialogBody: HTMLBodyElement | null = CKEditorDialogIFrameDocument.querySelector(
        'body.model-equationpluginmodel'
      )
      // check if the dialog is an for editing djangocms-equations
      if (EquationEditDialogBody !== null) {
        const SaveEquationBtn: HTMLAnchorElement | null = RootIFrameDocument.querySelector(
          '.cms-ckeditor-dialog .cke_dialog_ui_button_ok'
        )
        if (SaveEquationBtn !== null) {
          if (!SaveEquationBtn.classList.contains('listens-for-refresh')) {
            SaveEquationBtn.classList.add('listens-for-refresh')
            SaveEquationBtn.addEventListener('click', event => {
              debug_printer(true, "Rerendering Equations in CKEditor")
              setTimeout(
                () => CKEditor_render_equation(RootIFrame, 5),
                500
              )
            })
          }
        }
      }
    } else {
      if (max_runs >= 0) {
        debug_printer(
          true,
          'max_runs=',
          max_runs,
          '\nCKEditorDialogIFrame was null or content was null',
          CKEditorDialogIFrame
        )
        setTimeout(
          () => CKEditor_render_equation(RootIFrame, max_runs - 1),
          500
        )
      }
    }
  }

  const CKEditor_render_equation = (
    RootIFrame: HTMLIFrameElement,
    max_runs = 10,
    date = new Date()
  ) => {
    debug_printer(true, ' running TextPlugin_render_equation')
    if (iframe_is_loaded(RootIFrame)) {
      // const RootIFrameDocument: HTMLDocument = RootIFrame.contentDocument
      CKEditor_render_equation_normal(RootIFrame, max_runs)
      CKEditor_bind_rerender(RootIFrame, max_runs)
    } else {
      if (max_runs >= 0) {
        debug_printer(
          true,
          'max_runs=',
          max_runs,
          date,
          '\niframe1 was null or content was null',
          RootIFrame
        )
        setTimeout(
          () => CKEditor_render_equation(RootIFrame, max_runs - 1, date),
          500
        )
      }
    }
  }
  // original from:
  // https://stackoverflow.com/a/49023264/3990615
  const body_mutation_observer_callback = (records: any) => {
    records.forEach(function(record: any) {
      let AddedNodeList = record.addedNodes
      let i = AddedNodeList.length - 1

      for (; i > -1; i--) {
        let AddedNode = AddedNodeList[i]
        if (AddedNode.nodeName === 'IFRAME') {
          debug_printer(true, 'RootIFrame added\n', AddedNode)
          CKEditor_render_equation(AddedNode)
        }
      }
    })
  }

  let body_mutation_observer = new MutationObserver(
    body_mutation_observer_callback
  )

  let targetNode = document.body

  body_mutation_observer.observe(targetNode, { childList: true, subtree: true })

  // edit dialog visable
  // document.querySelector("iframe").contentDocument.querySelector(".cke_dialog_body").offsetParent
})
