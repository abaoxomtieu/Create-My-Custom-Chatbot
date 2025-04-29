# from fastapi import APIRouter, UploadFile, File, Form, HTTPException
# from fastapi.responses import JSONResponse
# import base64

# from src.agents.image_explainer.func import image_explainer

# router = APIRouter(prefix="/image-explainer", tags=["Image Explainer"])


# @router.post("/explain")
# async def explain_image(
#     image: UploadFile = File(...),
#     domain: str = Form("Môn Toán"),
#     topic: str = Form("Toán Tích Phân và Giải thích"),
#     question: str = Form("Giải thích cách giải")
# ):
#     """
#     Endpoint to explain an image based on domain, topic and question.
    
#     Parameters:
#     - image: The image file to analyze
#     - domain: The domain/field related to the image
#     - topic: The specific topic within the domain
#     - question: The question about the image
    
#     Returns:
#     - JSON response with the explanation
#     """
#     try:
#         # Read and convert image to base64
#         image_content = await image.read()
#         base64_image = base64.b64encode(image_content).decode("utf-8")
        
        
#         response = await image_explainer(base64_image, domain, topic, question)
        
#         return JSONResponse(
#             content={"result": response},
#             status_code=200
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
