# Backend Gemini AI service providing comprehensive Gemini client with support for Pro, Pro Vision, and Flash models
import os
import logging
from typing import Dict, List, Optional, Any, AsyncIterator
from datetime import datetime
import json

try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("Google Generative AI library not available. Install with: pip install google-generativeai")

from app.config import settings

logger = logging.getLogger(__name__)

class GeminiService:
    """Comprehensive Gemini AI service with support for multiple models and capabilities"""
    
    def __init__(self):
        self.api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY", "")
        self.model_name = settings.gemini_model
        self.vision_model_name = settings.gemini_vision_model
        self.flash_model_name = settings.gemini_flash_model
        
        self.models: Dict[str, Any] = {}
        self.is_initialized = False
        
        if GEMINI_AVAILABLE and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.is_initialized = True
                logger.info("Gemini AI service initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini AI: {e}")
                self.is_initialized = False
        else:
            logger.warning("Gemini AI not available - API key missing or library not installed")
    
    def _get_model(self, model_type: str = "pro") -> Optional[Any]:
        """Get a Gemini model instance"""
        if not self.is_initialized:
            return None
        
        model_key = f"{model_type}_model"
        if model_key in self.models:
            return self.models[model_key]
        
        try:
            if model_type == "vision":
                model = genai.GenerativeModel(self.vision_model_name)
            elif model_type == "flash":
                model = genai.GenerativeModel(self.flash_model_name)
            else:
                model = genai.GenerativeModel(self.model_name)
            
            self.models[model_key] = model
            return model
        except Exception as e:
            logger.error(f"Failed to get Gemini model {model_type}: {e}")
            return None
    
    async def generate_text(
        self,
        prompt: str,
        model_type: str = "pro",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        system_instruction: Optional[str] = None
    ) -> Optional[str]:
        """Generate text using Gemini"""
        model = self._get_model(model_type)
        if not model:
            return None
        
        try:
            generation_config = {
                "temperature": temperature,
            }
            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens
            
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }
            
            if system_instruction:
                model = genai.GenerativeModel(
                    model.model_name if hasattr(model, 'model_name') else self.model_name,
                    system_instruction=system_instruction,
                    generation_config=generation_config,
                    safety_settings=safety_settings
                )
            else:
                model = genai.GenerativeModel(
                    model.model_name if hasattr(model, 'model_name') else self.model_name,
                    generation_config=generation_config,
                    safety_settings=safety_settings
                )
            
            response = await model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error generating text with Gemini: {e}")
            return None
    
    async def analyze_image(
        self,
        image_data: bytes,
        prompt: str,
        mime_type: str = "image/jpeg"
    ) -> Optional[str]:
        """Analyze image using Gemini Vision"""
        model = self._get_model("vision")
        if not model:
            return None
        
        try:
            import PIL.Image
            import io
            
            image = PIL.Image.open(io.BytesIO(image_data))
            
            response = await model.generate_content_async([prompt, image])
            return response.text
        except Exception as e:
            logger.error(f"Error analyzing image with Gemini Vision: {e}")
            return None
    
    async def generate_stream(
        self,
        prompt: str,
        model_type: str = "pro",
        temperature: float = 0.7
    ) -> AsyncIterator[str]:
        """Generate streaming text response"""
        model = self._get_model(model_type)
        if not model:
            return
        
        try:
            generation_config = {
                "temperature": temperature,
            }
            
            model = genai.GenerativeModel(
                model.model_name if hasattr(model, 'model_name') else self.model_name,
                generation_config=generation_config
            )
            
            response = await model.generate_content_async(prompt, stream=True)
            
            async for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error(f"Error in streaming generation: {e}")
    
    async def function_calling(
        self,
        prompt: str,
        functions: List[Dict[str, Any]],
        model_type: str = "pro"
    ) -> Optional[Dict[str, Any]]:
        """Use Gemini function calling for tool usage"""
        model = self._get_model(model_type)
        if not model:
            return None
        
        try:
            # Convert functions to Gemini function declarations
            tools = [{"function_declarations": functions}]
            
            response = await model.generate_content_async(
                prompt,
                tools=tools
            )
            
            # Extract function calls from response
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'function_call'):
                        return {
                            "function_name": part.function_call.name,
                            "arguments": dict(part.function_call.args)
                        }
            
            return None
        except Exception as e:
            logger.error(f"Error in function calling: {e}")
            return None
    
    async def analyze_mission_requirements(
        self,
        mission_description: str,
        mission_type: str,
        target_area: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Analyze mission requirements using Gemini"""
        prompt = f"""
        Analyze the following mission requirements and provide a detailed plan:
        
        Mission Type: {mission_type}
        Description: {mission_description}
        Target Area: {json.dumps(target_area, indent=2)}
        
        Provide:
        1. Required resources
        2. Optimal agent selection
        3. Estimated duration
        4. Risk assessment
        5. Success criteria
        
        Return as JSON.
        """
        
        response = await self.generate_text(prompt, model_type="pro", temperature=0.3)
        if not response:
            return None
        
        try:
            # Try to extract JSON from response
            json_match = response.find("{")
            if json_match != -1:
                json_str = response[json_match:]
                json_end = json_str.rfind("}")
                if json_end != -1:
                    return json.loads(json_str[:json_end+1])
        except Exception as e:
            logger.error(f"Error parsing mission analysis: {e}")
        
        return {"analysis": response}
    
    async def detect_anomalies(
        self,
        data: Dict[str, Any],
        context: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Detect anomalies in environmental data using Gemini"""
        prompt = f"""
        Analyze the following environmental data for anomalies:
        
        {json.dumps(data, indent=2)}
        
        {f"Context: {context}" if context else ""}
        
        Identify:
        1. Anomalies or unusual patterns
        2. Risk level (low, medium, high, critical)
        3. Recommended actions
        4. Confidence score
        
        Return as JSON.
        """
        
        response = await self.generate_text(prompt, model_type="pro", temperature=0.2)
        if not response:
            return None
        
        try:
            json_match = response.find("{")
            if json_match != -1:
                json_str = response[json_match:]
                json_end = json_str.rfind("}")
                if json_end != -1:
                    return json.loads(json_str[:json_end+1])
        except Exception as e:
            logger.error(f"Error parsing anomaly detection: {e}")
        
        return {"anomalies": response}
    
    async def reason_about_mission(
        self,
        mission_data: Dict[str, Any],
        agent_capabilities: List[str]
    ) -> Optional[Dict[str, Any]]:
        """Use Gemini for intelligent mission reasoning"""
        prompt = f"""
        Given the following mission and agent capabilities, provide intelligent reasoning:
        
        Mission: {json.dumps(mission_data, indent=2)}
        Agent Capabilities: {', '.join(agent_capabilities)}
        
        Provide:
        1. Best approach for mission execution
        2. Potential challenges
        3. Optimization suggestions
        4. Expected outcomes
        
        Return as JSON.
        """
        
        response = await self.generate_text(prompt, model_type="pro", temperature=0.5)
        if not response:
            return None
        
        try:
            json_match = response.find("{")
            if json_match != -1:
                json_str = response[json_match:]
                json_end = json_str.rfind("}")
                if json_end != -1:
                    return json.loads(json_str[:json_end+1])
        except Exception as e:
            logger.error(f"Error parsing mission reasoning: {e}")
        
        return {"reasoning": response}
    
    def is_available(self) -> bool:
        """Check if Gemini service is available"""
        return self.is_initialized

# Global instance
gemini_service = GeminiService()

