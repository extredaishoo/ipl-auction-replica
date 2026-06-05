import os
import random
from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client

app = Flask(__name__)
CORS(app)  # Allows your hosted frontend website to safely communicate with this backend

# Your exact, verified Supabase Cloud Database credentials
SUPABASE_URL = "https://toopwqxypkeoudxzcdqw.supabase.co"
SUPABASE_KEY = "sb_publishable_p8rFCr_KDxq2SWXbd6XlSQ_7lEPpchK"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/api/draw', methods=['GET'])
def draw_player():
    target_cat = request.args.get('category')
    
    try:
        # Fetch only available (UNSOLD) players in the selected category from the cloud
        response = supabase.table("players").select("*").eq("category", target_cat).eq("status", "UNSOLD").execute()
        players = response.data

        if not players:
            return jsonify({"error": "No players available left in this selection set deck pool."}), 404
            
        # Select a random player from the pool
        selected_player = random.choice(players)
        return jsonify({
            "id": selected_player["id"],
            "name": selected_player["name"],
            "category": selected_player["category"],
            "base_price": float(selected_player["base_price"])
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sell', methods=['POST'])
def sell_player():
    req = request.json
    player_id = req['id']
    team = req['team']
    price = req['price']

    try:
        if team == "UNSOLD":
            # Update database status to UNSOLD
            supabase.table("players").update({"status": "UNSOLD"}).eq("id", player_id).execute()
        else:
            # Update database status to SOLD along with team and final price
            supabase.table("players").update({
                "status": "SOLD", 
                "sold_to": team, 
                "sold_price": price
            }).eq("id", player_id).execute()

        return jsonify({"status": "completed"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Cloud hosts like Render require binding to 0.0.0.0 and reading a dynamic port
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
