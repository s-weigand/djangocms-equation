import { render } from "katex";
import renderMathInElement from "katex/dist/contrib/auto-render";

const debug_printer = (debug = true, ...args: any[]) => {
  if (process.env.NODE_ENV === "development" && debug) {
    // Or, `process.env.NODE_ENV !== 'production'`
    // Only runs in development and will be stripped from production build.
    console.log(...args);
  }
};

export const init_render_main_page = (debug = false) => {
  document.addEventListener("DOMContentLoaded", function(event) {
    renderMathInElement(document.body, {
      delimiters: [
        { left: "$$", right: "$$", display: true },
        { left: "\\[", right: "\\]", display: true },
        { left: "$", right: "$", display: false },
        { left: "\\(", right: "\\)", display: false }
      ]
    });

    debug_printer(debug, "page loaded");
    let cms_btn = document.querySelector(
      ".cms-toolbar-item-cms-mode-switcher a"
    ) as HTMLAnchorElement;
    const render_all = () => {
      // TODO:
      // needs to be done for ".model-equationpluginmodel a" aswell
      let structure_side_bar = document.querySelector(
        ".cms-structure-content"
      ) as HTMLDivElement;
      // check if the element is visible
      if (structure_side_bar.offsetParent !== null) {
        debug_printer(debug, "cms_btn clicked => rendering all");
        renderMathInElement(structure_side_bar, {
          throwOnError: false
        });
      } else {
        debug_printer(debug, "need delay");
        setTimeout(render_all, 100);
      }
    };
    debug_printer(debug, cms_btn);
    cms_btn.onclick = render_all;
  });
};

export const init_live_editor_render = (debug = false) => {
  document.addEventListener("DOMContentLoaded", function(event) {
    let tex_in = document.getElementById("id_tex_code") as HTMLTextAreaElement;
    let tex_out = document.getElementById(
      "katex_live_render_out"
    ) as HTMLSpanElement;
    const render_text = () => {
      let tex_code = tex_in.value;
      debug_printer(debug, "tex_code to render: ", tex_code);
      render(tex_code, tex_out, {
        throwOnError: false
      });
    };

    tex_in.oninput = render_text;
    render_text();
  });
};
