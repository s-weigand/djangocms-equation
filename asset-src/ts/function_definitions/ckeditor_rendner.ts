import {
  debug_printer,
  render_full_page,
} from './djangocms_equation'

// Abstract mutation observer definitions

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
interface args_add_mutation_observer extends baseArgsGenerateMutationCallback {
  targetBodyElement: Node | HTMLElement
  observerSettings?: MutationObserverInit
}

const generateMutationCallback = ({
  nodeCallbacks,
  debugName = 'observerDebugName',
  debug = false,
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
  debug = false,
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

// Concrete implementations for the CkEditor implementations

const CKEditor_render_equation = (RootIFrameNode: Node, debug = false) => {
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
                debug_printer(debug, '#### IFRAME created\n', foo)
              },
            ],
          },
        ],
        debug: debug,
        debugName: 'RootIFrameBody observer',
      })
    }
  }
}

const CKEditor_render_equation_normal = (
  ChildIFrameNode: Node,
  debug = false
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
              },
            ],
          },
        ],
        debug: debug,
        debugName: 'EditorIFrame observer',
      })
    }
  }
}
const render_spans = (targetBody: HTMLBodyElement) => {
  let katex_spans = targetBody.querySelectorAll('span.katex')
  if (katex_spans.length !== 0) {
    render_full_page(targetBody)
    // removes the class cke_widget_inline from the grandparent span
    // of span.katex which leads to the equiation being displayed
    // as if it was floating left in the texteditor.
    // But in normal render it would be centered.
    let i = katex_spans.length - 1
    for (; i > -1; i--) {
      let cke_grand_parent_span = (katex_spans[i].parentElement as HTMLElement)
        .parentElement as HTMLSpanElement
      if (cke_grand_parent_span.classList.contains('cke_widget_inline')) {
        cke_grand_parent_span.classList.remove('cke_widget_inline')
      }
    }
  }
}

export const init_ckeditor_rendering = (debug = false) => {
  add_mutation_observer({
    targetBodyElement: document.body,
    nodeCallbacks: [
      { nodeName: 'IFRAME', callbackFuncs: [CKEditor_render_equation] },
      {
        nodeName: 'P',
        callbackFuncs: [
          foo => {
            render_spans(document.body as HTMLBodyElement)
          },
        ],
      },
    ],
    debug: debug,
    debugName: 'document.body observer',
  })
}
