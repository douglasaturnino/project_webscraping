import requests


def featch_page():
    url = "https://lista.mercadolivre.com.br/celulares-telefones/celulares-smartphones/iphone/linha-iphone-16/iphone-16-pro/iphone-16_NoIndex_True#applied_filter_id%3DMODEL%26applied_filter_name%3DModelo%26applied_filter_order%3D3%26applied_value_id%3D41937253%26applied_value_name%3DiPhone+16+Pro%26applied_value_order%3D3%26applied_value_results%3D23%26is_custom%3Dfalse"
    response = requests.get(url)
    return response.text


if __name__ == "__main__":
    page_content = featch_page()
