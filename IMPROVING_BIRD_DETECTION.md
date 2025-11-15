# Improving Bird Detection for Denmark

## Current Setup
- Using YOLOv5n (nano) pre-trained on COCO dataset
- Generic "bird" class (ID: 14)
- Works but may miss Danish-specific species or small birds

## Options (Easiest → Most Effective)

### Option 1: Use Better Pre-trained Model (Easiest)
**YOLOv8n** is newer and often better at bird detection:
- More accurate than YOLOv5n
- Still lightweight for Pi 3B+
- No training needed

**Implementation:** Just change model name in code

---

### Option 2: Fine-tune on Danish Bird Images (Recommended)
**Best balance of effort vs. results**

**What you need:**
- 200-500 images of Danish birds (common species: sparrows, robins, crows, seagulls, etc.)
- Label them with bounding boxes (use tools like LabelImg or Roboflow)
- Fine-tune YOLOv5n for 50-100 epochs

**Steps:**
1. Collect images from your camera captures
2. Label them (draw boxes around birds)
3. Split into train/val (80/20)
4. Fine-tune model on your Mac/cloud
5. Export to `.pt` file
6. Load custom model on Pi

**Time:** 2-4 hours of labeling + training time

---

### Option 3: Use Specialized Bird Detection Model
**Models trained specifically on birds:**
- **iNaturalist models** (many bird species)
- **eBird/Cornell models** (bird-focused)
- **Custom Danish bird dataset** (if available)

**Challenge:** May be larger/heavier than YOLOv5n

---

### Option 4: Multi-Class Detection (Advanced)
**Detect specific Danish bird species:**
- Instead of just "bird", detect: "sparrow", "robin", "crow", "seagull", etc.
- Requires more training data per species
- More useful for wildlife monitoring

---

### Option 5: Improve Preprocessing
**Better image quality = better detection:**
- Increase resolution (if Pi can handle it)
- Better lighting/positioning
- Image enhancement (contrast, sharpening)
- Multiple frames + voting

---

## Quick Wins (No Training Required)

1. **Lower confidence threshold** (already done - 0.10)
2. **Use YOLOv8n instead of YOLOv5n** (better accuracy, same size)
3. **Test different input sizes** (640x640 vs 640x480)
4. **Use image augmentation** (brightness, contrast adjustments)

---

## Recommended Approach for WingSight

**Phase 1 (Now):** Switch to YOLOv8n - easy, immediate improvement

**Phase 2 (Next):** Collect 100-200 images from your camera, label them, fine-tune

**Phase 3 (Later):** If needed, train multi-class model for specific Danish species

---

## Resources

- **Labeling tools:** LabelImg, Roboflow, CVAT
- **Training:** Use your Mac or Google Colab (free GPU)
- **Datasets:** 
  - **Danish Bird Dataset (Skagen & Klim)** - [Download here](https://demo.researchdata.se/en/catalogue/dataset/2021-316-1) - Real Danish birds from wind farms, already annotated! Perfect for fine-tuning.
  - iNaturalist, eBird, Danish bird photography sites
- **Fine-tuning guide:** Ultralytics documentation

### Danish Bird Dataset (Recommended!)

**Annotated birds dataset for object detection using deep learning, Skagen & Klim**
- **Location:** Skagen Grey Lighthouse & Klim Fjordeholme, Denmark
- **Format:** Images + bounding box annotations (LabelImg format)
- **Use case:** Originally for wind farm bird detection
- **Perfect for:** Fine-tuning YOLOv8n for Danish birds
- **Access:** Freely available at researchdata.se

**Citation:** Alqaysi, H., Fedorov, I., Qureshi, Faisal. Z., & O'Nils, M. (2021). A temporal boosted yolo-based model for birds detection around wind farms. Journal of Imaging, 7(11), 227.

