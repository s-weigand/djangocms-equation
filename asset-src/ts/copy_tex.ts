/**
 * This nearly identical code as in 'katex/contrib/copy-tex/copy-tex.js'.
 * With the key difference being, that additional newline and whitespace characters,
 * which are added due to a problem of ckeditor with inline equations, are stripped.
 */
// @ts-ignore
import katexReplaceWithTex from 'katex/contrib/copy-tex/katex2tex'

/**
 * Function to strip additional newline character which were added incorrectly.
 *
 * @param tex_code Latex code to be striped from too many new line character
 */

const replace_empty_lines = (tex_code: string) => {
  return tex_code.replace(/(\n\s*[\n\s]+\n)/g, '\n\n')
}

// Global copy handler to modify behavior on .katex elements.
document.addEventListener('copy', function(event: ClipboardEvent) {
  const selection = window.getSelection() as Selection
  if (selection.isCollapsed) {
    return // default action OK if selection is empty
  }
  const fragment = selection.getRangeAt(0).cloneContents()
  if (!fragment.querySelector('.katex-mathml')) {
    return // default action OK if no .katex-mathml elements
  }
  // Preserve usual HTML copy/paste behavior.
  const html = []
  for (let i = 0; i < fragment.childNodes.length; i++) {
    let childNode: HTMLElement = fragment.childNodes[i] as HTMLElement
    html.push(childNode.outerHTML)
  }
  const clipboardData: DataTransfer | null = event.clipboardData
  if (clipboardData !== null) {
    clipboardData.setData('text/html', html.join(''))
    // Rewrite plain-text version.
    clipboardData.setData(
      'text/plain',
      replace_empty_lines(katexReplaceWithTex(fragment).textContent)
    )
  }
  // Prevent normal copy handling.
  event.preventDefault()
})
