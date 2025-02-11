// Actions taken on page load and resize to maintain viewport
import Constants from "./constants.js"

function calculateViewportOffsets() {
    // Set the CSS variables for real/virtual pixel ratio and vertical
    // and horizontal offset. Should be called on page load and resize
    let width = window.innerWidth;
    let height = window.innerHeight;
    let dimension = Math.min(width, height);

    let style = document.documentElement.style;
    style.setProperty(
        "--pvpratio", `${dimension / Constants.VGRID_DIMENSION}px`
    );
    style.setProperty(
        "--hoffset", `${(width - dimension) / 2}px`
    );
    style.setProperty(
        "--voffset", `${(height - dimension) / 2}px`
    );
}

export default calculateViewportOffsets;
