const API_BASE_URL = "http://localhost:8000/conversations";

export const createAndUpdateOrder = async (text: string) => {
  try {
    const response = await fetch(`${API_BASE_URL}/create_and_update`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json",
      },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Error in createAndUpdateOrder:", error);
    throw error;
  }
};
