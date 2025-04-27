from flask import redirect, url_for
from flask import Blueprint, request, jsonify, Flask, render_template, g
from datetime import datetime, timedelta
import jwt
import os
from functools import wraps
from .utils import token_required
from cachetools import TTLCache
import requests
from flasgger import Swagger, swag_from
from .config import SECRET_KEY
from .cred import username_1, password_1

# Create a cache with 1-hour TTL
coins_cache = TTLCache(maxsize=100, ttl=3600)

main_bp = Blueprint("main", __name__)

@main_bp.route('/', methods=['GET'])
def index():
    return redirect(url_for('main.login_page'))


@main_bp.route('/login', methods=['GET'])
def login_page():
    token = request.cookies.get('token')
    if token:
        try:
            # Verify token is valid
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return redirect(url_for('main.dashboard'))
        except jwt.InvalidTokenError:
            # If token is invalid, show login page
            return render_template('login.html')
    return render_template('login.html')


@main_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Missing JSON data'}), 401
        
        username = data.get('username')
        password = data.get('password')
        
        if username == username_1  and password == password_1:
            token_payload = {
                'user': username,
                'exp': datetime.utcnow() + timedelta(hours=24)
            }
            
            token = jwt.encode(
                token_payload,
                SECRET_KEY,
                algorithm='HS256'
            )
            
            response = jsonify({
                'message': 'Login successful',
                'token': token
            })
            
            # Modified cookie settings - remove max_age to make it a session cookie
            response.set_cookie(
                'token', 
                token,
                httponly=True,
                secure=False,  # Set to True in production with HTTPS
                samesite='Lax',
                # Remove max_age parameter to make it a session cookie
            )
            
            return response, 200
            
        return jsonify({'message': 'Please Enter Valid Credentials'}), 401
        
    except Exception as e:
        print(f"Error in login route: {str(e)}")
        return jsonify({'message': 'Server error', 'error': str(e)}), 500

            
@main_bp.route('/dashboard')
@token_required
def dashboard():
    return render_template('dashboard.html')



@main_bp.route("/coins", methods=["GET"])
@token_required
def coins():
    try:
        print("\nAccessing coins endpoint")
        print(f"Request headers: {dict(request.headers)}")
        
        # Get query parameters
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)
        currency = request.args.get('currency', default='usd', type=str).lower()
        
        # Create cache key
        cache_key = f"{currency}_{page}_{per_page}"
        
        # Try to get data from cache first
        cached_data = coins_cache.get(cache_key)
        if cached_data:
            print("Returning cached data")
            return jsonify(cached_data)

        # If not in cache, fetch from CoinGecko
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            'vs_currency': currency,
            'order': 'market_cap_desc',
            'per_page': per_page,
            'page': page,
            'sparkline': False,
            'price_change_percentage': '24h'
        }
        
        # Add headers to avoid rate limiting
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        print(f"Fetching data from CoinGecko with params: {params}")
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            coins_data = response.json()
            formatted_coins = []
            
            for coin in coins_data:
                formatted_coin = {
                    'id': coin['id'],
                    'symbol': coin['symbol'].upper(),
                    'name': coin['name'],
                    'current_price': coin['current_price'],
                    'market_cap': coin['market_cap'],
                    'market_cap_rank': coin['market_cap_rank'],
                    'price_change_24h': coin['price_change_percentage_24h']
                }
                formatted_coins.append(formatted_coin)
            
            result = {
                'coins': formatted_coins,
                'page': page,
                'per_page': per_page,
                'currency': currency
            }
            
            # Store in cache
            coins_cache[cache_key] = result
            
            return jsonify(result)
            
        elif response.status_code == 429:
            print("Rate limit exceeded from CoinGecko")
            
            # Return dummy data when rate limited
            dummy_data = {
                'coins': [
                    {
                        'id': 'bitcoin',
                        'symbol': 'BTC',
                        'name': 'Bitcoin',
                        'current_price': 50000,
                        'market_cap': 1000000000000,
                        'market_cap_rank': 1,
                        'price_change_24h': 2.5
                    },
                    {
                        'id': 'ethereum',
                        'symbol': 'ETH',
                        'name': 'Ethereum',
                        'current_price': 3000,
                        'market_cap': 350000000000,
                        'market_cap_rank': 2,
                        'price_change_24h': 1.8
                    }
                    # Add more dummy coins as needed
                ],
                'page': page,
                'per_page': per_page,
                'currency': currency,
                'note': 'Rate limited - showing sample data'
            }
            return jsonify(dummy_data), 200
            
        else:
            print(f"Error from CoinGecko API: {response.status_code}")
            return jsonify({
                'error': f'Error fetching data: {response.status_code}',
                'message': 'Unable to fetch real-time data'
            }), response.status_code
            
    except requests.exceptions.RequestException as e:
        print(f"Request error: {str(e)}")
        return jsonify({
            'error': 'Failed to fetch data from CoinGecko',
            'message': str(e)
        }), 503
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({
            'error': str(e),
            'message': 'Internal server error'
        }), 500



@main_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

from flask import make_response  # Add this import at the top

@main_bp.route('/logout')
def logout():
    try:
        response = make_response(redirect(url_for('main.login_page')))
        
        # Clear the token cookie
        response.delete_cookie('token')
        
        # Clear any session data
        if hasattr(g, 'current_user'):
            delattr(g, 'current_user')
            
        return response
        
    except Exception as e:
        print(f"Error during logout: {str(e)}")
        return redirect(url_for('main.login_page'))
