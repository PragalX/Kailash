from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/get_results', methods=['GET'])
def get_results():
    # Get the URL from query parameters
    url = request.args.get('url')
    
    if not url:
        return jsonify({"error": "URL parameter is missing"}), 400
    
    headers = {
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    # Send the GET request
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return jsonify({"error": f"Failed to retrieve data, status code: {response.status_code}"}), 500
    
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extracting specific information
    result_info = {
        "University": soup.find("p", style="text-transform:uppercase;text-align:center; font-weight:bold;").text.strip(),
        "Student Name": soup.find(id="ContentPlaceHolder1_DataList1_StudentNameLabel_0").text.strip(),
        "Father's Name": soup.find(id="ContentPlaceHolder1_DataList1_FatherNameLabel_0").text.strip(),
        "Mother's Name": soup.find(id="ContentPlaceHolder1_DataList1_MotherNameLabel_0").text.strip(),
        "College": soup.find(id="ContentPlaceHolder1_DataList1_CollegeNameLabel_0").text.strip(),
        "Course": soup.find(id="ContentPlaceHolder1_DataList1_CourseLabel_0").text.strip(),
    }
    
    # Extract SGPA, CGPA, Remarks, and Publish Date
    sgpa = soup.find(id="ContentPlaceHolder1_DataList5_GROSSTHEORYTOTALLabel_0").text.strip()
    cgpa = soup.select_one("#ContentPlaceHolder1_GridView3 td:last-child").text.strip()
    remarks = soup.find(id="ContentPlaceHolder1_DataList3_remarkLabel_0").text.strip() if soup.find(id="ContentPlaceHolder1_DataList3_remarkLabel_0") else "N/A"
    publish_date = soup.select_one("#ContentPlaceHolder1_DataList3 td:last-child").text.strip()
    
    # Update result info with additional fields
    result_info.update({
        "SGPA": sgpa,
        "CGPA": cgpa,
        "Remarks": remarks,
        "Publish Date": publish_date,
    })
    
    # Extracting theory subject results
    theory_results = []
    theory_table = soup.find(id="ContentPlaceHolder1_GridView1")
    for row in theory_table.find_all("tr")[1:]:
        cols = row.find_all("td")
        theory_results.append({
            "Subject Code": cols[0].text.strip(),
            "Subject Name": cols[1].text.strip(),
            "ESE": cols[2].text.strip(),
            "IA": cols[3].text.strip(),
            "Total": cols[4].text.strip(),
            "Grade": cols[5].text.strip(),
            "Credit": cols[6].text.strip(),
        })

    # Extracting practical subject results
    practical_results = []
    practical_table = soup.find(id="ContentPlaceHolder1_GridView2")
    for row in practical_table.find_all("tr")[1:]:
        cols = row.find_all("td")
        practical_results.append({
            "Subject Code": cols[0].text.strip(),
            "Subject Name": cols[1].text.strip(),
            "ESE": cols[2].text.strip(),
            "IA": cols[3].text.strip(),
            "Total": cols[4].text.strip(),
            "Grade": cols[5].text.strip(),
            "Credit": cols[6].text.strip(),
        })
    
    # Combine all data into one dictionary
    result_data = {
        "Result Info": result_info,
        "Theory Results": theory_results,
        "Practical Results": practical_results
    }
    
    return jsonify(result_data)


@app.route('/api', methods=['GET'])
def api_home():
    return "@Pragyan"

if __name__ == '__main__':
    app.run(debug=True)
