import { debug_printer, render_full_page } from './djangocms_equation'

// Abstract mutation observer definitions

interface NodeCallback {
  callbackFuncs: ((targetNode: Node) => void)[]
  nodeName: string
}

interface BaseArgsGenerateMutationCallback {
  nodeCallbacks: NodeCallback[]
  debugName?: string
  debug?: boolean
}
interface ArgsGenerateMutationCallback
  extends BaseArgsGenerateMutationCallback {
  parentNode: Node | HTMLElement
}
interface ArgsAddMutationObserver extends BaseArgsGenerateMutationCallback {
  targetBodyElement: Node | HTMLElement
  observerSettings?: MutationObserverInit
}

const generateMutationCallback = ({
  nodeCallbacks,
  debugName = 'observerDebugName',
  debug = false,
}: ArgsGenerateMutationCallback): MutationCallback => {
  const mutation_callback = (records: MutationRecord[]) => {
    debug_printer(debug, `running MutationCallback ${debugName}`)
    records.forEach(function(record: MutationRecord) {
      let addedNodeList = record.addedNodes
      let i = addedNodeList.length - 1
      for (; i > -1; i--) {
        let addedNode = addedNodeList[i]
        // debug_printer(debug, `new element`, AddedNode)
        for (let nodeCallback of nodeCallbacks) {
          if (addedNode.nodeName === nodeCallback.nodeName) {
            for (let callbackFunc of nodeCallback.callbackFuncs) {
              debug_printer(
                debug,
                `new ${nodeCallback.nodeName} added\n`,
                addedNode
              )

              callbackFunc(addedNode)
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
}: ArgsAddMutationObserver) => {
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

const CKEditor_render_equation = (rootIFrameNode: Node, debug = false) => {
  debug_printer(debug, '# running CKEditor_render_equation')
  debug_printer(debug, '## rootIFrameNode', rootIFrameNode)
  var rootIFrame = rootIFrameNode as HTMLIFrameElement

  rootIFrame.onload = () => {
    var rootIFrameBody = (rootIFrame.contentDocument as HTMLDocument).body
    debug_printer(debug, '### RootIFrame loaded')
    const childIFrame = rootIFrameBody.querySelector('iframe')
    if (childIFrame !== null) {
      debug_printer(debug, '#### ChildIFrame exists')
      CKEditor_render_equation_normal(childIFrame)
    } else {
      debug_printer(debug, '#### ChildIFrame exists NOT')
      add_mutation_observer({
        targetBodyElement: rootIFrameBody,
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
        debugName: 'rootIFrameBody observer',
      })
    }
  }
}

const CKEditor_render_equation_normal = (
  childIFrameNode: Node,
  debug = false
) => {
  debug_printer(debug, 'running CKEditor_render_equation_normal')
  const childIFrame = childIFrameNode as HTMLIFrameElement
  debug_printer(debug, 'childIFrame', childIFrame)
  debug_printer(debug, 'childIFrame.classList', childIFrame.classList)
  if (childIFrame.classList.contains('cke_wysiwyg_frame')) {
    const editorIFrame = childIFrame
    debug_printer(debug, 'editorIFrame', editorIFrame)

    editorIFrame.onload = () => {
      debug_printer(debug, 'editorIFrame iframe_is_loaded')
      const editorIFrameBody = (editorIFrame.contentDocument as HTMLDocument)
        .body as HTMLBodyElement
      render_spans(editorIFrameBody)
      add_mutation_observer({
        targetBodyElement: editorIFrameBody,
        nodeCallbacks: [
          {
            nodeName: 'SPAN',
            callbackFuncs: [
              foo => {
                render_spans(editorIFrameBody)
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
