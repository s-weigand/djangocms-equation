import SelectorObserver, { observe, Observer } from 'selector-observer'

import { debug_printer, render_elements_in_target } from './djangocms_equation'

const render_span = (katex_span: HTMLSpanElement) => {
  // removes the class cke_widget_inline from the grandparent span
  // of span.katex which leads to the equation being displayed
  // as if it was floating left in the text editor.
  // But in normal render it would be centered.
  render_elements_in_target(katex_span)
  let cke_grand_parent_span = (katex_span.parentElement as HTMLElement)
    .parentElement as HTMLSpanElement
  if (cke_grand_parent_span.classList.contains('cke_widget_inline')) {
    cke_grand_parent_span.classList.remove('cke_widget_inline')
  }
}

interface ObserverCollection {
  ObserverContainer: SelectorObserver | null
  Observer: Observer | null
}

const defaultObserverCollection: ObserverCollection = {
  ObserverContainer: null,
  Observer: null,
}

const iframe_observer_factory = (
  observerCollection: ObserverCollection,
  child_selector: string,
  add_callback: (element: HTMLIFrameElement) => void,
  debug = false
) => (iframe: HTMLIFrameElement) => {
  iframe.onload = () => {
    observerCollection.ObserverContainer = new SelectorObserver(
      iframe.contentDocument as HTMLDocument
    )
    observerCollection.Observer = observerCollection.ObserverContainer.observe(
      child_selector,
      {
        add(element) {
          debug_printer(debug, `${child_selector} added`, element)
          add_callback(element as HTMLIFrameElement)
        },
      }
    )
  }

  return
}

export const init_ckeditor_rendering = (debug = false) => {
  const outerObserverCollection = { ...defaultObserverCollection }
  const cke_wysiwygObserverCollection = { ...defaultObserverCollection }

  const cke_wysiwygObserver = iframe_observer_factory(
    cke_wysiwygObserverCollection,
    'span.katex',
    render_span,
    debug
  )
  const outerIframeObserver = iframe_observer_factory(
    outerObserverCollection,
    'iframe.cke_wysiwyg_frame',
    cke_wysiwygObserver,
    debug
  )
  observe('iframe', {
    add(iframe) {
      outerIframeObserver(iframe as HTMLIFrameElement)
    },
    remove(iframe) {
      debug_printer(debug, 'Outer iframe  deleted')
      outerObserverCollection.Observer?.abort()
      cke_wysiwygObserverCollection.Observer?.abort()
    },
  })
}
