import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import zipfile

# Page configuration
st.set_page_config(
    page_title="Image to Cartoon Converter",
    page_icon="🎨",
    layout="wide"
)

st.title("🎨 Image to Cartoon Converter")
st.caption("🖼️ Convert images to 5 cartoon styles • ⬇️ Download individual or all at once")

# Cartoon conversion functions
def edge_preserving(img):
    smooth = cv2.bilateralFilter(img, 9, 75, 75)
    gray = cv2.cvtColor(smooth, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY, 9, 2
    )
    color = cv2.bilateralFilter(img, 9, 200, 200)
    return cv2.bitwise_and(color, color, mask=edges)

def color_quantization(img):
    data = np.float32(img).reshape((-1, 3))
    _, labels, centers = cv2.kmeans(
        data, 8, None,
        (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.001),
        10, cv2.KMEANS_RANDOM_CENTERS
    )
    centers = np.uint8(centers)
    quantized = centers[labels.flatten()].reshape(img.shape)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY, 9, 2
    )
    return cv2.bitwise_and(quantized, quantized, mask=edges)

def stylization(img):
    return cv2.stylization(img, sigma_s=150, sigma_r=0.25)

def pencil_sketch(img):
    _, sketch = cv2.pencilSketch(
        img, sigma_s=60, sigma_r=0.07, shade_factor=0.05
    )
    return sketch

def advanced_cartoon(img):
    smooth = img.copy()
    for _ in range(3):
        smooth = cv2.bilateralFilter(smooth, 9, 75, 75)

    data = np.float32(smooth).reshape((-1, 3))
    _, labels, centers = cv2.kmeans(
        data, 12, None,
        (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.001),
        10, cv2.KMEANS_RANDOM_CENTERS
    )
    centers = np.uint8(centers)
    quantized = centers[labels.flatten()].reshape(img.shape)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 7)
    edges = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY, 9, 3
    )
    return cv2.bitwise_and(quantized, quantized, mask=edges)

MODELS = {
    "🧩 Edge Preserving": edge_preserving,
    "🎯 Color Quantization": color_quantization,
    "✨ Stylization": stylization,
    "✏️ Pencil Sketch": pencil_sketch,
    "🔥 Advanced Cartoon": advanced_cartoon
}

# File upload
uploaded_file = st.file_uploader(
    "📤 Upload Image",
    type=["jpg", "jpeg", "png", "webp", "bmp"]
)

def download_button(img_array, filename):
    buf = io.BytesIO()
    Image.fromarray(img_array).save(buf, format="PNG")
    st.download_button(
        "⬇️ Download",
        buf.getvalue(),
        filename,
        "image/png"
    )

# Main application logic
if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    original = np.array(image)
    img_cv = cv2.cvtColor(original, cv2.COLOR_RGB2BGR)

    if st.button("🎬 Convert to Cartoon"):
        with st.spinner("⚙️ Processing..."):
            results = {"🖼️ Original": original}

            for name, func in MODELS.items():
                out = func(img_cv)
                results[name] = cv2.cvtColor(out, cv2.COLOR_BGR2RGB)

            st.divider()
            st.subheader("📸 Results")

            cols = st.columns(6)
            for i, (name, img) in enumerate(results.items()):
                with cols[i]:
                    st.write(name)
                    st.image(img, use_container_width=True)
                    download_button(
                        img,
                        f"{name.lower().replace(' ', '_').replace('🧩','').replace('🎯','').replace('✨','').replace('✏️','').replace('🔥','').strip()}.png"
                    )

            # Create ZIP archive with all outputs
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for name, img in results.items():
                    if "Original" not in name:
                        img_buf = io.BytesIO()
                        Image.fromarray(img).save(img_buf, format="PNG")
                        zip_file.writestr(
                            f"{name.lower().replace(' ', '_')}.png",
                            img_buf.getvalue()
                        )

            st.divider()
            st.download_button(
                "📦 Download All 5 Cartoon Outputs",
                zip_buffer.getvalue(),
                "all_cartoon_outputs.zip",
                "application/zip",
                use_container_width=True
            )
else:
    st.info("👆 Upload an image to start")

st.divider()
st.caption("⬇️ Download individual outputs or all 5 at once")