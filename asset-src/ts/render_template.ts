import {
  init_render_main_page,
  debug_printer,
  render_full_page,
} from './djangocms_equation'

init_render_main_page(false)

// just for debugging
document.addEventListener('DOMContentLoaded', function(event) {
  // RootIFrame
  // document.querySelector("iframe")
  // EditorIFrame
  // document.querySelector("iframe").contentDocument.querySelector("iframe.cke_wysiwyg_frame cke_reset")

  // document.querySelector("iframe").contentWindow.CKEDITOR
  // CKEDITOR.scriptLoader

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

  // const CKEditor_render_equation_normal = (
  //   RootIFrame: HTMLIFrameElement,
  //   max_runs: number
  // ) => {
  const CKEditor_render_equation_normal = (
    ChildIFrameNode: Node,
    parentNode: Node,
    max_runs: number = 5
  ) => {
    debug_printer(true, 'running CKEditor_render_equation_normal')
    // const RootIFrameDocument = RootIFrame.contentDocument as HTMLDocument
    // let EditorIFrame: HTMLIFrameElement | null = RootIFrameDocument.querySelector(
    //   'iframe.cke_wysiwyg_frame'
    // ) as HTMLIFrameElement
    const ChildIFrame = ChildIFrameNode as HTMLIFrameElement
    debug_printer(true, "ChildIFrame", ChildIFrame)
    debug_printer(true, "ChildIFrame.classList", ChildIFrame.classList)
    if (ChildIFrame.classList.contains('cke_wysiwyg_frame')) {
      const EditorIFrame = ChildIFrame
      debug_printer(true, "EditorIFrame", EditorIFrame)

      if (iframe_is_loaded(EditorIFrame)) {
        debug_printer(true, "EditorIFrame iframe_is_loaded")
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
            () =>
              CKEditor_render_equation_normal(
                ChildIFrameNode,
                parentNode,
                max_runs - 1
              ),
            500
          )
          // setTimeout(
          //   () => CKEditor_render_equation(RootIFrame, RootIFrame, max_runs - 1),
          //   500
          // )
        }
      }
    }
    // setTimeout(
    //   () =>
    //     CKEditor_render_equation_normal(
    //       ChildIFrameNode,
    //       parentNode,
    //       max_runs - 1
    //     ),
    //   500
    // )
  }

  const CKEditor_bind_rerender = (
    RootIFrame: HTMLIFrameElement,
    parentNode: Node,
    max_runs: number
  ) => {
    debug_printer(true, ' running CKEditor_bind_rerender')

    const RootIFrameDocument = RootIFrame.contentDocument as HTMLDocument
    debug_printer(
      true,
      '## btn is ',
      RootIFrameDocument.querySelector(
        '.cms-ckeditor-dialog .cke_dialog_ui_button_ok'
      )
    )
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
              debug_printer(true, 'Rerendering Equations in CKEditor')
              setTimeout(
                () => CKEditor_bind_rerender(RootIFrame, parentNode, 5),
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
          () => CKEditor_bind_rerender(RootIFrame, parentNode, max_runs - 1),
          500
        )
      }
    }
  }

  const CKEditor_render_equation = (
    RootIFrameNode: Node,
    parentNode: Node,
    max_runs = 5,
    date = new Date()
  ) => {
    debug_printer(true, ' running CKEditor_render_equation')
    debug_printer(true, 'RootIFrameNode', RootIFrameNode)
    const RootIFrame = RootIFrameNode as HTMLIFrameElement

    if (
      RootIFrame !== null &&
      RootIFrame.contentDocument !== null &&
      RootIFrame.contentDocument.body !== null
    ) {
      RootIFrame.onload = () => {
        const RootIFrameBody: Node = RootIFrame.contentDocument.body as Node
        console.log('loaded RootIFrame', RootIFrame.contentDocument.body)
        console.log('## spans', RootIFrame.contentDocument.querySelectorAll(".katex"))
        console.log('## iframe', RootIFrame.contentDocument.querySelectorAll("iframe"))
        add_mutation_observer({
          targetBodyElement: RootIFrameBody,
          nodeCallbacks: [
            {
              nodeName: 'IFRAME',
              callbackFuncs: [CKEditor_render_equation_normal],
            },
            {
              nodeName: 'DIV',
              callbackFuncs: [(foo, bar)=>{console.log("#### div created\n",foo, bar)}],
            },
          ],
          debugName: 'RootIFrameBody observer',
        })
        // CKEditor_render_equation_normal(RootIFrame.contentDocument.querySelector("iframe"), RootIFrame)
      }
      let RootIFrame2 = document.querySelector('iframe') as HTMLElement
      debug_printer(true, 'RootIFrameBody', RootIFrameBody)
      setTimeout(() => {
        debug_printer(
          true,
          'RootIFrameBody2 delayed',
          document.querySelector('iframe')
        )
      }, 200)
    }
    // if (iframe_is_loaded(RootIFrame)) {
    //   CKEditor_render_equation_normal(RootIFrame, document.body, max_runs)
    //   // CKEditor_render_equation_normal(RootIFrame, max_runs)
    //   // CKEditor_bind_rerender(RootIFrame, RootIFrame, max_runs)
    //   const dummyCallback = (newNode: Node, parentNode: Node) => {
    //     // console.log("## running dummyCallback", newNode)
    //     const classList: DOMTokenList = (newNode as HTMLDivElement).classList
    //     if (
    //       classList.contains('cke_dialog_body') ||
    //       classList.contains('cms-ckeditor-dialog')
    //     ) {
    //       CKEditor_bind_rerender(RootIFrame, RootIFrame, max_runs)
    //       console.log('###new DIV cke_dialog_body', newNode)
    //       console.log('##classList', (newNode as HTMLDivElement).classList)
    //     }
    //   }
    //   add_mutation_observer({
    //     targetBodyElement: (RootIFrame.contentDocument as HTMLDocument).body,
    //     nodeCallbacks: [
    //       {
    //         nodeName: 'DIV',
    //         callbackFuncs: [dummyCallback],
    //       },
    //     ],
    //   })
    // } else {
    //   if (max_runs >= 0) {
    //     debug_printer(
    //       true,
    //       'max_runs=',
    //       max_runs,
    //       date,
    //       '\niframe1 was null or content was null',
    //       RootIFrame
    //     )
    //     setTimeout(() => {
    //       CKEditor_render_equation(
    //         RootIFrame,
    //         document.body,
    //         max_runs - 1,
    //         date
    //       )
    //     }, 500)
    //   }
    // }
  }
  // original from:
  // https://stackoverflow.com/a/49023264/3990615
  // const body_mutation_observer_callback = (records: MutationRecord[]) => {
  //   records.forEach(function(record: MutationRecord) {
  //     let AddedNodeList = record.addedNodes
  //     let i = AddedNodeList.length - 1

  //     for (; i > -1; i--) {
  //       let AddedNode = AddedNodeList[i]
  //       if (AddedNode.nodeName === 'IFRAME') {
  //         debug_printer(true, 'RootIFrame added\n', AddedNode)
  //         debug_printer(true, 'record.attributeName', record.type)
  //         CKEditor_render_equation(AddedNode)
  //       }
  //     }
  //   })
  // }

  interface NodeCallback {
    callbackFuncs: ((
      targetNode: Node,
      parentNode: Node | HTMLElement
    ) => void)[]
    nodeName: string
  }

  interface baseArgsGenerateMutationCallback {
    nodeCallbacks: NodeCallback[]
    debugName?: string
    debug?: boolean
  }
  interface argsGenerateMutationCallback
    extends baseArgsGenerateMutationCallback {
    parentNode: Node | HTMLElement
  }
  interface args_add_mutation_observer
    extends baseArgsGenerateMutationCallback {
    targetBodyElement: Node | HTMLElement
    observerSettings?: MutationObserverInit
  }

  const generateMutationCallback = ({
    nodeCallbacks,
    parentNode,
    debugName = 'observerDebugName',
    debug = true,
  }: argsGenerateMutationCallback): MutationCallback => {
    const mutation_callback = (records: MutationRecord[]) => {
      debug_printer(debug, `running MutationCallback ${debugName}`)
      records.forEach(function(record: MutationRecord) {
        let AddedNodeList = record.addedNodes
        let i = AddedNodeList.length - 1
        for (; i > -1; i--) {
          let AddedNode = AddedNodeList[i]
          // debug_printer(debug, `new element`, AddedNode)
          for (let nodeCallback of nodeCallbacks) {
            if (AddedNode.nodeName === nodeCallback.nodeName) {
              for (let callbackFunc of nodeCallback.callbackFuncs) {
                debug_printer(
                  debug,
                  `new ${nodeCallback.nodeName} added\n`,
                  AddedNode
                )

                callbackFunc(AddedNode, parentNode)
              }
            }
          }
        }
      })
    }
    return mutation_callback
  }

  /**
   * Function providing a faster abstracted way to add a MutationObserver
   *
   * @param param0
   */
  const add_mutation_observer = ({
    targetBodyElement,
    nodeCallbacks,
    debugName = 'observerDebugName',
    debug = true,
    observerSettings = {
      childList: true,
      subtree: true,
    },
  }: args_add_mutation_observer) => {
    var callbackFunc = generateMutationCallback({
      nodeCallbacks,
      parentNode: targetBodyElement,
      debugName,
      debug,
    })
    var mutation_observer = new MutationObserver(callbackFunc)

    mutation_observer.observe(targetBodyElement, observerSettings)
  }
  add_mutation_observer({
    targetBodyElement: document.body,
    nodeCallbacks: [
      { nodeName: 'IFRAME', callbackFuncs: [CKEditor_render_equation] },
    ],
    debugName: 'document.body observer',
  })
  var dclick = new MouseEvent('dblclick', {
    'view': window,
    'bubbles': true,
    'cancelable': true
  });
(document.querySelector("p span.katex") as HTMLSpanElement).dispatchEvent(dclick);

  // let body_mutation_observer = new MutationObserver(
  //   body_mutation_observer_callback
  // )

  // let targetNode = document.body

  // body_mutation_observer.observe(targetNode, { childList: true, subtree: true })

  // edit dialog visable
  // document.querySelector("iframe").contentDocument.querySelector(".cke_dialog_body").offsetParent
})
