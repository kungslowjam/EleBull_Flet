import onnx

# Path to the input ONNX model
input_model_path = r"C:\Users\hello\Desktop\Project_me\EleBull_Flet\model\yolov8n.onnx"

# Path to save the updated ONNX model
output_model_path = r"C:\Users\hello\Desktop\Project_me\EleBull_Flet\model\yolov8n_ir9.onnx"

# Load the ONNX model
model = onnx.load(input_model_path)

# Update the IR version
model.ir_version = 9

# Save the modified model
onnx.save(model, output_model_path)

print(f"Model IR version changed to 9 and saved as {output_model_path}")
