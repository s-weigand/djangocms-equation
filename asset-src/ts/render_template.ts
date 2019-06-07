import {
  init_render_main_page,
  debug_printer,
  render_full_page,
} from './djangocms_equation'

// init_render_main_page(false)
console.log("foooooooooooooooooooooo")

if (document.readyState === 'complete') {
  console.log("compleate")
  init_render_main_page(false)
} else {
  document.addEventListener('DOMContentLoaded', function(event) {
    console.log("DOMContentLoaded triggered")
    init_render_main_page(false)
  })
}

// just for debugging
// document.addEventListener('DOMContentLoaded', function(event) {
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

  const CKEditor_render_equation_normal = (
    ChildIFrameNode: Node,
    debug = true
  ) => {
    debug_printer(debug, 'running CKEditor_render_equation_normal')
    const ChildIFrame = ChildIFrameNode as HTMLIFrameElement
    debug_printer(debug, 'ChildIFrame', ChildIFrame)
    debug_printer(debug, 'ChildIFrame.classList', ChildIFrame.classList)
    if (ChildIFrame.classList.contains('cke_wysiwyg_frame')) {
      const EditorIFrame = ChildIFrame
      debug_printer(debug, 'EditorIFrame', EditorIFrame)

      EditorIFrame.onload = () => {
        debug_printer(debug, 'EditorIFrame iframe_is_loaded')
        const EditorIFrameBody = (EditorIFrame.contentDocument as HTMLDocument)
          .body as HTMLBodyElement
        render_spans(EditorIFrameBody)
        add_mutation_observer({
          targetBodyElement: EditorIFrameBody,
          nodeCallbacks: [
            {
              nodeName: 'SPAN',
              callbackFuncs: [
                foo => {
                  render_spans(EditorIFrameBody)
                  console.log('#### new span', foo)
                },
              ],
            },
          ],
          debugName: 'EditorIFrame observer',
        })
      }
    }
  }
  const render_spans = (targetBody: HTMLBodyElement) => {
    console.log('## ran render_spans')
    let katex_spans = targetBody.querySelectorAll('span.katex')
    if (katex_spans.length !== 0) {
      render_full_page(targetBody)
      // removes the class cke_widget_inline from the grandparent span
      // of span.katex which leads to the equiation being displayed
      // as if it was floating left in the texteditor.
      // But in normal render it would be centered.
      let i = katex_spans.length - 1
      for (; i > -1; i--) {
        let cke_grand_parent_span = (katex_spans[i]
          .parentElement as HTMLElement).parentElement as HTMLSpanElement
        if (cke_grand_parent_span.classList.contains('cke_widget_inline')) {
          cke_grand_parent_span.classList.remove('cke_widget_inline')
        }
      }
    }
  }

  const CKEditor_render_equation = (RootIFrameNode: Node, debug = true) => {
    debug_printer(debug, '# running CKEditor_render_equation')
    debug_printer(debug, '## RootIFrameNode', RootIFrameNode)
    var RootIFrame = RootIFrameNode as HTMLIFrameElement

    RootIFrame.onload = () => {
      var RootIFrameBody = (RootIFrame.contentDocument as HTMLDocument).body
      debug_printer(debug, '### RootIFrame loaded')
      const ChildIFrame = RootIFrameBody.querySelector('iframe')
      if (ChildIFrame !== null) {
        debug_printer(debug, '#### ChildIFrame exists')
        CKEditor_render_equation_normal(ChildIFrame)
      } else {
        debug_printer(debug, '#### ChildIFrame exists NOT')
        add_mutation_observer({
          targetBodyElement: RootIFrameBody,
          nodeCallbacks: [
            {
              nodeName: 'IFRAME',
              callbackFuncs: [
                CKEditor_render_equation_normal,
                foo => {
                  console.log('#### IFRAME created\n', foo)
                },
              ],
            },
          ],
          debugName: 'RootIFrameBody observer',
        })
      }
    }
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
    callbackFuncs: ((targetNode: Node) => void)[]
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

                callbackFunc(AddedNode)
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
      {
        nodeName: 'P',
        callbackFuncs: [
          foo => {
            render_spans(document.body as HTMLBodyElement)
            console.log('#### new span', foo)
          },
        ],
      },
    ],
    debugName: 'document.body observer',
  })
  // render_spans(document.body as HTMLBodyElement)
  // var dclick = new MouseEvent('dblclick', {
  //   view: window,
  //   bubbles: true,
  //   cancelable: true,
  // })
  // ;(document.querySelector('p span.katex') as HTMLSpanElement).dispatchEvent(
  //   dclick
  // )

  // let body_mutation_observer = new MutationObserver(
  //   body_mutation_observer_callback
  // )

  // let targetNode = document.body

  // body_mutation_observer.observe(targetNode, { childList: true, subtree: true })

  // edit dialog visable
  // document.querySelector("iframe").contentDocument.querySelector(".cke_dialog_body").offsetParent
// })
