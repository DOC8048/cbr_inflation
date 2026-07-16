import pandas as pd
import requests
from xml.etree import ElementTree as ET
from datetime import datetime

def get_inflation(start_date='2013-01-01', end_date=None):
    """
    Получает данные по инфляции (индекс потребительских цен) с сайта ЦБ РФ.
    Возвращает pandas Series с индексом из дат и значениями инфляции (в процентах).
    """
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    url = "https://cbr.ru/secinfo/secinfo.asmx"
    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": "http://web.cbr.ru/InflationXML"
    }
    
    body = f'''<?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                   xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                   xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
      <soap:Body>
        <InflationXML xmlns="http://web.cbr.ru/">
          <DateFrom>{start_date}</DateFrom>
          <DateTo>{end_date}</DateTo>
        </InflationXML>
      </soap:Body>
    </soap:Envelope>'''
    
    response = requests.post(url, data=body, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Ошибка HTTP: {response.status_code}")
    
    root = ET.fromstring(response.content)
    
    # Данные лежат в тегах <RI>
    data = []
    for item in root.findall('.//RI'):
        dts_elem = item.find('DTS')
        inf_elem = item.find('infVal')
        if dts_elem is not None and inf_elem is not None:
            # Дата в формате MM.YYYY, превратим в datetime (первый день месяца)
            month, year = dts_elem.text.split('.')
            date_str = f"{year}-{month}-01"
            date = pd.to_datetime(date_str)
            value = float(inf_elem.text.replace(',', '.'))
            data.append({'date': date, 'value': value})
    
    # Если не нашли, попробуем с пространством имён (на случай, если потребуется)
    if not data:
        ns = {'cbr': 'http://web.cbr.ru/'}
        for item in root.findall('.//cbr:RI', ns):
            dts_elem = item.find('cbr:DTS', ns)
            inf_elem = item.find('cbr:infVal', ns)
            if dts_elem is not None and inf_elem is not None:
                month, year = dts_elem.text.split('.')
                date_str = f"{year}-{month}-01"
                date = pd.to_datetime(date_str)
                value = float(inf_elem.text.replace(',', '.'))
                data.append({'date': date, 'value': value})
    
    if not data:
        print("Не удалось найти данные. Проверьте структуру XML.")
        print(response.text[:1000])
        return None
    
    df = pd.DataFrame(data)
    df = df.sort_values('date').reset_index(drop=True)
    result = df.set_index('date')['value']
    return result

# Пример использования
if __name__ == "__main__":
    inf = get_inflation('2020-01-01')
    if inf is not None:
        # print(inf.tail())
        print(f"Инфляция: {inf.iloc[-1]:.2f}%")
    else:
        print("Данные не получены.")