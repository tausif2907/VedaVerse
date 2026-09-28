import fitz  # PyMuPDF for PDF manipulation

def find_and_replace_image(page, target_image_name, replacement_image_data):
    print(f"Looking for image to replace: {target_image_name}")
    images = page.get_images(full=True)
    for img in images:
        xref = img[0]
        rects = page.get_image_rects(xref)
        if not rects:
            continue
        rect = rects[0]
        print(f"Replacing image at xref {xref} with new image data.")
        page.delete_image(xref)
        page.insert_image(rect, stream=replacement_image_data)

def update_text_on_pdf(page, new_text, doc):
    """
    Replace the existing text on a PDF page with new text.
    If the new text overflows, add the remaining text to subsequent pages.

    Args:
        page: The current page object.
        new_text: The new text to add.
        doc: The PDF document object for adding new pages.
    """
    print("Updating text on PDF page.")

    fontname = "Helvetica"
    fontsize = 12
    line_spacing = fontsize * 1.2  # Line spacing multiplier

    # Extract text blocks and their bounding boxes
    text_instances = page.get_text("blocks")
    content_boxes = [fitz.Rect(inst[:4]) for inst in text_instances]

    # Sort bounding boxes by their top-left corner (y-coordinates)
    content_boxes.sort(key=lambda r: (r.y0, r.x0))

    # Redact (remove) existing content
    for bbox in content_boxes:
        page.add_redact_annot(bbox, fill=(1, 1, 1))  # White out the old content
    page.apply_redactions()

    # Insert new text into the cleared areas
    remaining_text = new_text
    for bbox in content_boxes:
        if not remaining_text.strip():
            break  # No more text to add

        text_to_fit, remaining_text = fit_text_to_box(remaining_text, bbox, fontsize, fontname, line_spacing)
       
        # Insert the portion of text that fits in the current bounding box
        page.insert_textbox(
            bbox,
            text_to_fit,
            fontsize=fontsize,
            color=(0, 0, 0),
            align=fitz.TEXT_ALIGN_LEFT,
        )

    # Handle overflow by adding remaining text to new pages
    if remaining_text.strip():
        content_box = fitz.Rect(72, 72, 540, 720)  # Standard area for new pages
        while remaining_text.strip():
            new_page = doc.new_page()  # Create a new page
            text_to_fit, remaining_text = fit_text_to_box(remaining_text, content_box, fontsize, fontname, line_spacing)
           
            new_page.insert_textbox(
                content_box,
                text_to_fit,
                fontsize=fontsize,
                color=(0, 0, 0),
                align=fitz.TEXT_ALIGN_LEFT,
            )
            print(f"Overflow text added to a new page. Remaining text length: {len(remaining_text)}")

    print("Text update complet`ed.")


def fit_text_to_box(text, bbox, fontsize, fontname="Helvetica", line_spacing=14.4):
    """
    Determine how much of the text fits in a given bounding box.
    Returns:
        - The portion of text that fits in the box.
        - The remaining text that doesn't fit.
    """
    max_width, max_height = bbox.width, bbox.height
    lines = []
    remaining_text = text
    words = text.split()
    current_line = ""
    total_height = 0

    for word in words:
        test_line = f"{current_line} {word}".strip()
        text_width = fitz.Font(fontname).text_length(test_line, fontsize=fontsize)

        if text_width <= max_width:
            current_line = test_line
        else:
            # Line exceeds width, add the current line to lines and reset
            lines.append(current_line)
            total_height += line_spacing
            current_line = word

            # Check if the box height has been exceeded
            if total_height + line_spacing > max_height:
                break

    # Add the final line if it fits
    if current_line and total_height + line_spacing <= max_height:
        lines.append(current_line)

    # Prepare the fitted text and the remaining text
    fitted_text = "\n".join(lines)
    remaining_text = " ".join(words[len(" ".join(fitted_text.split()).split()):])

    return fitted_text, remaining_text