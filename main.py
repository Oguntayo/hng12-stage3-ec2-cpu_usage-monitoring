from fastapi import FastAPI, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import requests

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

def is_perfect(n: int) -> bool:
    if n < 2:
        return False
    divisors = [i for i in range(1, n) if n % i == 0]
    return sum(divisors) == n

def armstrong(number: int):
    digits = [int(digit) for digit in str(number)]
    total_num_of_digits = len(digits)
    armstrong_sum = sum(digit ** total_num_of_digits for digit in digits)
    return {
        "is_armstrong": armstrong_sum == number,
        "digit_sum": sum(digits)
    }

def error_response():
    """Returns a JSON error response for missing or invalid input."""
    return JSONResponse(
        content={"number": "alphabet", "error": True},
        status_code=status.HTTP_400_BAD_REQUEST
    )

@app.get("/classify-number")
def classify_number(number: str = Query(None)):
    if number is None:
        return error_response()
    
    try:
        num = int(number)
    except ValueError:
        return error_response()
    
    armstrong_result = armstrong(num)
    number_properties = ["armstrong"] if armstrong_result["is_armstrong"] else []
    number_properties.append("odd" if num % 2 != 0 else "even")

    try:
        response = requests.get(f'http://numbersapi.com/{num}?json')
        response.raise_for_status()
        fun_fact = response.json().get('text', f"No fun fact available for {num}")
    except requests.exceptions.RequestException:
        fun_fact = f"No fun fact available for {num}"

    return JSONResponse(
        content={
            "number": num,
            "is_prime": is_prime(num),
            "is_perfect": is_perfect(num),
            "properties": number_properties,
            "digit_sum": armstrong_result["digit_sum"],
            "fun_fact": fun_fact
        },
        status_code=status.HTTP_200_OK
    )
