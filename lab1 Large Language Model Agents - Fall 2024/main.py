from typing import Dict, List
from autogen import ConversableAgent
import sys
import os
from math import sqrt

config_list = {
    "model": "gpt-4o",
    "api_key": os.environ.get("4omini_api"),
    "api_type": "azure",
    "base_url": os.environ.get("4omini_endpoint"),
    "api_version": "2024-12-01-preview",
}

def fetch_restaurant_data(restaurant_name: str) -> Dict[str, List[str]]:
    # TODO
    # This function takes in a restaurant name and returns the reviews for that restaurant. 
    # The output should be a dictionary with the key being the restaurant name and the value being a list of reviews for that restaurant.
    # The "data fetch agent" should have access to this function signature, and it should be able to suggest this as a function call. 
    # Example:
    # > fetch_restaurant_data("Applebee's")
    # {"Applebee's": ["The food at Applebee's was average, with nothing particularly standing out.", ...]}
    with open("E:\\program\\agent\\lab1 Large Language Model Agents - Fall 2024\\restaurant-data.txt", "r") as file:
        lines = file.readlines()
    restaurant_name = restaurant_name.replace("-", " ")
    for line in lines:
        line_ = line.lower()
        line_ = line_.replace("-", " ")
        if restaurant_name.lower() in line_:
            return line

    pass


def calculate_overall_score(restaurant_name: str, food_scores: List[int], customer_service_scores: List[int]) -> Dict[str, float]:
    # TODO
    # This function takes in a restaurant name, a list of food scores from 1-5, and a list of customer service scores from 1-5
    # The output should be a score between 0 and 10, which is computed as the following:
    # SUM(sqrt(food_scores[i]**2 * customer_service_scores[i]) * 1/(N * sqrt(125)) * 10
    # The above formula is a geometric mean of the scores, which penalizes food quality more than customer service. 
    # Example:
    # > calculate_overall_score("Applebee's", [1, 2, 3, 4, 5], [1, 2, 3, 4, 5])
    # {"Applebee's": 5.048}
    # NOTE: be sure to that the score includes AT LEAST 3  decimal places. The public tests will only read scores that have 
    # at least 3 decimal places.
    overall_scores = []
    for i in range(len(food_scores)):
        overall_score = sqrt(food_scores[i]**2 * customer_service_scores[i]) * 1/(len(food_scores) * sqrt(125))
        overall_scores.append(overall_score)
    overall_score = sum(overall_scores) * 10
    return {restaurant_name: round(overall_score, 3)}
    pass

def get_data_fetch_agent_prompt(restaurant_query: str) -> str:
    # TODO
    # It may help to organize messages/prompts within a function which returns a string. 
    # For example, you could use this function to return a prompt for the data fetch agent 
    # to use to fetch reviews for a specific restaurant.
    query = restaurant_query
    system_message = f"Get the restaurant reviews from {query}. Use review_analysis_agent and scoring_agent to get the final score. The final output format should be: \" The average score for 'restaurant_name' is 'score'.\" Attention: YOU MUSTN'T DO ANY CALCULATIONS YOURSELF. " 
    return system_message, query
# TODO: feel free to write as many additional functions as you'd like.

# Do not modify the signature of the "main" function.
def main(user_query: str, config_list = config_list) -> None:
    system_message, user_query = get_data_fetch_agent_prompt(user_query)
    entrypoint_agent_system_message = f"{system_message}" # TODO
    # example LLM config for the entrypoint agent
    llm_config = {"config_list": config_list,}
    # the main entrypoint/supervisor agent
    entrypoint_agent = ConversableAgent("entrypoint_agent", 
                                        system_message=entrypoint_agent_system_message, 
                                        llm_config=llm_config,
                                        human_input_mode="NEVER",
                                        )
    
    data_fetch_agent = ConversableAgent("data_fetch_agent",
                                        system_message="This agent fetches the reviews for a specific restaurant. " \
                                        "The output should be a dictionary with the key being the restaurant name and the value being a list of reviews for that restaurant."\
                                        "The output should be in the format: \"restaurant_name: 'restaurant_name', food_reviews: 'review', service_reviews: 'review'\".",
                                        llm_config=llm_config,
                                        human_input_mode="NEVER",
                                        )
    data_fetch_agent.register_for_llm(name="fetch_restaurant_data", description="Fetches the reviews for a specific restaurant.")(fetch_restaurant_data)
    entrypoint_agent.register_for_execution(name="fetch_restaurant_data")(fetch_restaurant_data)

    # TODO
    # Create more agents here. 
    review_analysis_agent = ConversableAgent("review_analysis_agent",
                                        system_message="This agent fetches the food_score and the customer_service_score of given restaurant data." \
                                        "`food_score`: the quality of food at the restaurant. This will be a score from 1-5." \
                                        "`customer_service_score`: the quality of customer service at the restaurant. This will be a score from 1-5." \
                                        "Score 1/5 has one of these adjectives: awful, horrible, or disgusting." \
                                        "Score 2/5 has one of these adjectives: bad, unpleasant, or offensive." \
                                        "Score 3/5 has one of these adjectives: average, uninspiring, or forgettable." \
                                        "Score 4/5 has one of these adjectives: good, enjoyable, or satisfying." \
                                        "Score 5/5 has one of these adjectives: awesome, incredible, or amazing." \
                                        "example:The food at McDonald's was average, but the customer service was unpleasant. The uninspiring menu options were served quickly, but the staff seemed disinterested and unhelpful.We see that the food is described as \"average\", which corresponds to a `food_score` of 3. We also notice that the customer service is described as \"unpleasant\", which corresponds to a `customer_service_score` of 2. Therefore, the agent should be able to determine `food_score: 3` and `customer_service_score: 2` for this example review." \
                                        "The output should follow the format below:" \
                                        "restaurant_name: 'restaurant_name', food_score: 'score', customer_service_score: 'score'", 
                                        llm_config=llm_config,
                                        human_input_mode="NEVER",
                                        )
    
    scoreing_agent = ConversableAgent("scoreing_agent",
                                        system_message="This agent calculates the overall score of a restaurant based on the food_score and customer_service_score." \
                                        "You need to use calculate_overall_score function to calculate the overall score.", 
                                        llm_config=llm_config,
                                        human_input_mode="NEVER",
                                        )
    entrypoint_agent.register_for_execution(name="calculate_overall_score")(calculate_overall_score)
    scoreing_agent.register_for_llm(name="calculate_overall_score", description="Calculates the overall score of a restaurant based on the food_score and customer_service_score.")(calculate_overall_score)


    # TODO
    # Fill in the argument to `initiate_chats` below, calling the correct agents sequentially.
    # If you decide to use another conversation pattern, feel free to disregard this code.
    
    # Uncomment once you initiate the chat with at least one agent.
    # result = entrypoint_agent.initiate_chats([{}])
    result = entrypoint_agent.initiate_chats(
        [
            {
                "recipient": data_fetch_agent,
                "message": f"Get the reviews for {user_query}. Just return the reviews in the format: \"restaurant_name: 'restaurant_name', food_reviews: 'review', service_reviews: 'review'\".",
                "max_turns": 2,
                "summary_method": "last_msg",
            },
            {
                "recipient": review_analysis_agent,
                "message": f"According to the reviews, please provide the food_score and customer_service_score for {user_query}. Just return the scores in the format: \"restaurant_name: 'restaurant_name', food_score: 'score', customer_service_score: 'score'\".",
                "max_turns": 1,
                "summary_method": "last_msg",
            },
            {
                "recipient": scoreing_agent,
                "message": f"Calculate the overall score for {user_query}. Also the replied score should be numbers that have 3 or more decimal places.",
                "max_turns": 2,
                "summary_method": "last_msg",
            },
        ]
    )
    
# DO NOT modify this code below.
if __name__ == "__main__":
    # assert len(sys.argv) > 1, "Please ensure you include a query for some restaurant when executing main."
    # main(sys.argv[1])
    main("What is the overall score for In N Out?")