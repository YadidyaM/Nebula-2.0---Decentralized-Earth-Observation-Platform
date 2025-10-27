import { GoogleGenerativeAI } from "@google/generative-ai";
import { ChatMessage, VoiceCommand } from "../types";

class GeminiClient {
  private genAI: GoogleGenerativeAI | null = null;
  private model: any = null;
  private apiKey: string;

  constructor() {
    this.apiKey = import.meta.env.VITE_GEMINI_API_KEY || "";
    this.initializeClient();
  }

  private initializeClient() {
    if (!this.apiKey) {
      console.warn(
        "Gemini API key not provided. Voice commands and AI chat will be disabled."
      );
      return;
    }

    try {
      this.genAI = new GoogleGenerativeAI(this.apiKey);
      this.model = this.genAI.getGenerativeModel({ model: "gemini-pro" });
      console.log("Gemini AI client initialized");
    } catch (error) {
      console.error("Failed to initialize Gemini AI client:", error);
    }
  }

  // Voice Command Processing
  async processVoiceCommand(command: VoiceCommand): Promise<string> {
    if (!this.model) {
      return "AI service not available. Please check your API key.";
    }

    try {
      const prompt = this.buildVoiceCommandPrompt(command.text);
      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      const text = response.text();

      return this.formatResponse(text);
    } catch (error) {
      console.error("Error processing voice command:", error);
      return "Sorry, I encountered an error processing your command. Please try again.";
    }
  }

  private buildVoiceCommandPrompt(command: string): string {
    return `
You are an AI assistant for the Nebula Protocol, a decentralized Earth observation platform. 
Process the following voice command and provide a helpful response.

Voice Command: "${command}"

Context:
- This is an environmental monitoring system with AI agents
- Available mission types: forestry, cryosphere, disaster_management, security, weather, hydrology, urban_infrastructure, land_monitoring
- Available agents: Forest Guardian, Ice Sentinel, Storm Tracker, Urban Monitor, Water Watcher, Security Sentinel, Land Surveyor, Disaster Responder
- Users can create missions, check agent status, view telemetry data, and monitor environmental risks

Provide a helpful response that:
1. Acknowledges the command
2. Explains what action will be taken
3. Provides relevant information or next steps

Keep the response concise and professional, suitable for a mission control interface.
    `.trim();
  }

  // Chat Message Processing
  async processChatMessage(message: ChatMessage): Promise<string> {
    if (!this.model) {
      return "AI service not available. Please check your API key.";
    }

    try {
      const prompt = this.buildChatPrompt(message);
      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      const text = response.text();

      return this.formatResponse(text);
    } catch (error) {
      console.error("Error processing chat message:", error);
      return "Sorry, I encountered an error processing your message. Please try again.";
    }
  }

  private buildChatPrompt(message: ChatMessage): string {
    return `
You are an AI assistant for the Nebula Protocol mission control system. 
Respond to the following user message in a helpful and professional manner.

User Message: "${message.content}"
Message Type: ${message.type}
Timestamp: ${message.timestamp}

Context:
- This is a space-themed environmental monitoring platform
- Users can interact with AI agents, create missions, and monitor Earth observation data
- The interface has a holographic, futuristic design
- Available commands include mission creation, agent management, telemetry monitoring, and risk assessment

Provide a response that:
1. Is helpful and informative
2. Maintains the space/mission control theme
3. Offers relevant suggestions or next steps
4. Uses appropriate technical terminology

Keep the response concise and suitable for a mission control chat interface.
    `.trim();
  }

  // Mission Parameter Extraction
  async extractMissionParameters(naturalLanguage: string): Promise<any> {
    if (!this.model) {
      return null;
    }

    try {
      const prompt = `
Extract mission parameters from the following natural language request:

"${naturalLanguage}"

Return a JSON object with the following structure:
{
  "name": "Mission name",
  "type": "mission_type",
  "priority": "priority_level",
  "target_area": {
    "latitude": number,
    "longitude": number,
    "radius_km": number,
    "description": "Location description"
  },
  "assigned_agents": ["agent_type1", "agent_type2"]
}

Available mission types: forestry, cryosphere, disaster_management, security, weather, hydrology, urban_infrastructure, land_monitoring
Available priorities: low, medium, high, critical
Available agents: Forest Guardian, Ice Sentinel, Storm Tracker, Urban Monitor, Water Watcher, Security Sentinel, Land Surveyor, Disaster Responder

If any information is missing or unclear, use reasonable defaults or ask for clarification.
      `.trim();

      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      const text = response.text();

      // Try to parse JSON from the response
      try {
        const jsonMatch = text.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          return JSON.parse(jsonMatch[0]);
        }
      } catch (parseError) {
        console.error("Error parsing mission parameters JSON:", parseError);
      }

      return null;
    } catch (error) {
      console.error("Error extracting mission parameters:", error);
      return null;
    }
  }

  // Risk Analysis
  async analyzeRiskData(riskData: any): Promise<string> {
    if (!this.model) {
      return "AI analysis not available.";
    }

    try {
      const prompt = `
Analyze the following environmental risk data and provide insights:

${JSON.stringify(riskData, null, 2)}

Provide:
1. Risk assessment summary
2. Potential impacts
3. Recommended actions
4. Priority level

Keep the analysis concise and actionable for mission control operators.
      `.trim();

      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      const text = response.text();

      return this.formatResponse(text);
    } catch (error) {
      console.error("Error analyzing risk data:", error);
      return "Risk analysis failed. Please try again.";
    }
  }

  // Telemetry Analysis
  async analyzeTelemetryData(telemetryData: any): Promise<string> {
    if (!this.model) {
      return "AI analysis not available.";
    }

    try {
      const prompt = `
Analyze the following satellite telemetry data and provide insights:

${JSON.stringify(telemetryData, null, 2)}

Provide:
1. Data quality assessment
2. Notable patterns or anomalies
3. System health status
4. Recommendations

Keep the analysis technical but accessible for mission control operators.
      `.trim();

      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      const text = response.text();

      return this.formatResponse(text);
    } catch (error) {
      console.error("Error analyzing telemetry data:", error);
      return "Telemetry analysis failed. Please try again.";
    }
  }

  // Response Formatting
  private formatResponse(text: string): string {
    // Clean up the response text
    return text
      .trim()
      .replace(/^\*\*|\*\*$/g, "") // Remove markdown bold markers
      .replace(/\n{3,}/g, "\n\n") // Limit consecutive newlines
      .substring(0, 500); // Limit response length
  }

  // Utility Methods
  isAvailable(): boolean {
    return this.model !== null;
  }

  async testConnection(): Promise<boolean> {
    if (!this.model) {
      return false;
    }

    try {
      const result = await this.model.generateContent("Test connection");
      return true;
    } catch (error) {
      console.error("Gemini AI connection test failed:", error);
      return false;
    }
  }

  // Error Handling
  private handleError(error: any): never {
    console.error("Gemini AI error:", error);
    throw new Error(`AI service error: ${error.message}`);
  }
}

// Create singleton instance
export const geminiClient = new GeminiClient();
export default geminiClient;
