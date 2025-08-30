from docxtpl import DocxTemplate
from docx2pdf import convert
import json
from pathlib import Path

def load_context(json_path: str) -> dict:
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def render_template(template_path: str, context: dict, output_docx: str) -> None:
    doc = DocxTemplate(template_path)
    doc.render(context)
    doc.save(output_docx)

def convert_to_pdf(input_docx: str, output_pdf: str) -> None:
    # Convert the docx to PDF
    convert(input_docx, output_pdf)

def main():
    # templates = ["template1.docx", "template2.docx", "template3.docx"]
    templates = ["template1.docx"]
    data_path = "input_data.json"
    out_dir = "out"
    Path(out_dir).mkdir(exist_ok=True)

    context = load_context(data_path)

    for i, tpl in enumerate(templates, start=1):
        tpl_path = Path(tpl)
        if not tpl_path.exists():
            print(f"WARNING: {tpl} not found, skipping.")
            continue

        output_docx = Path(out_dir) / f"cv_template{i}_filled.docx"
        output_pdf  = Path(out_dir) / f"cv_template{i}_filled.pdf"

        # Fill template
        render_template(str(tpl_path), context, str(output_docx))
        print(f"Generated Word: {output_docx}")

        # Convert to PDF
        convert_to_pdf(str(output_docx), str(output_pdf))
        print(f"Generated PDF: {output_pdf}")

if __name__ == "__main__":
    main()
