import pdfplumber
import json
import os
import re

PDF_NAME = "driver-knowledge-test-questions-rider.pdf"
IMAGE_DIR = "quiz_images"

if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

def start_extract():
    all_questions = []
    
    with pdfplumber.open(PDF_NAME) as pdf:
        for page in pdf.pages:
            text_objects = page.extract_words()
            page_images = page.images
            
            q_anchors = []
            for word in text_objects:
                if re.match(r'^[A-Z]{2,4}\d+$', word['text']):
                    q_anchors.append({"id": word['text'], "top": word['top']})
            
            page_text = page.extract_text()
            if not page_text: continue
            lines = page_text.split('\n')
            
            current_q = None
            page_qs = []
            
            for line in lines:
                clean_line = line.strip()
                if not clean_line: continue
                
                id_match = re.match(r'^([A-Z]{2,4}\d+)', clean_line)
                if id_match:
                    if current_q: page_qs.append(current_q)
                    q_id = id_match.group(1)
                    q_top = next((a['top'] for a in q_anchors if a['id'] == q_id), 0)
                    current_q = {"id": q_id, "question": "", "options": [], "answer": 0, "top": q_top, "image": None}
                    continue

                if clean_line.startswith("-"):
                    if current_q is not None:
                        current_q["options"].append(clean_line[1:].strip())
                else:
                    if current_q is not None:
                        if not current_q["options"]:
                            content = clean_line.replace(current_q["id"], "").strip()
                            if content: current_q["question"] += " " + content
                        else:
                            current_q["options"][-1] += " " + clean_line

            if current_q: page_qs.append(current_q)

            # matching images
            for img in page_images:
                img_top = img["top"]
                target_q = None
                sorted_qs = sorted(page_qs, key=lambda x: x["top"])
                for i in range(len(sorted_qs)):
                    limit = sorted_qs[i+1]["top"] if i+1 < len(sorted_qs) else 9999
                    if sorted_qs[i]["top"] < img_top < limit:
                        target_q = sorted_qs[i]
                        break
                if target_q:
                    safe_name = f"q_{target_q['id']}.png"
                    try:
                        page.within_bbox((img["x0"], img["top"], img["x1"], img["bottom"])).to_image().save(os.path.join(IMAGE_DIR, safe_name))
                        target_q["image"] = safe_name
                    except: pass

            # 💡 Maintain order: Do not shuffle options; the first one (index 0) is the correct answer
            for q in page_qs:
                q["options"] = [opt.strip() for opt in q["options"] if opt.strip()]
                q["question"] = q["question"].strip()
                q["answer"] = 0 

            all_questions.extend(page_qs)

    # Final save to file
    with open("questions.json", "w", encoding="utf-8") as f:
        json.dump(all_questions, f, ensure_ascii=False, indent=4)
    
    print(f"✅ Done！ Processed {len(all_questions)} questions, strictly following the PDF order.")

if __name__ == "__main__":
    start_extract()