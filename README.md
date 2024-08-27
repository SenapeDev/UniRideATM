# UniRideATM

UniRideATM è un bot Telegram sviluppato per rispondere all'esigenza personale di monitorare gli orari dei bus che collegano la propria abitazione con l'università, e viceversa. Questo strumento fornisce informazioni puntuali e precise riguardanti le linee di trasporto pubblico interessate, gli orari dei bus, e una stima del tempo necessario per raggiungere la fermata in tempo utile.

---
## Obiettivi del progetto
L'obiettivo principale di UniRideATM è quello di semplificare il processo di pianificazione degli spostamenti quotidiani tra casa e università, ottimizzando i tempi di attesa e riducendo al minimo le incertezze legate agli orari dei mezzi pubblici.

### Funzionalità
- **Orari dei bus**: Il bot fornisce gli orari aggiornati delle linee di bus rilevanti per il percorso tra casa e università.
- **Calcolo del tempo di arrivo**: In base all'orario attuale, il bot calcola se è possibile raggiungere la fermata del bus in tempo partendo immediatamente.
- **Informazioni su misura**: L'utente riceve soltanto informazioni riguardo le linee che collegano le due mete.

## Tecnologie utilizzate
UniRideATM è stato sviluppato utilizzando Python, con il supporto della libreria `python-telegram-bot` per l'integrazione con Telegram. Le informazioni sugli orari dei bus sono state estrapolate direttamente dal sito delle *smart poles* dell'[ATM](https://www.atmmessinaspa.it/smartpoles2.php), e organizzate in modo da essere facilmente accessibili e comprensibili dall'utente.
## Installazione
Passaggi necessari per l’installazione e l’avvio di UniRideATM:
1. **Clonazione del repository**
   ```bash
   git clone https://github.com/SenapeDev/UniRideATM.git
   ``` 
2. **Accesso alla cartella del progetto**
   ```bash
   cd UniRideATM
   ``` 
3. **Installazione le dipendenze necessarie**
   ```bash
   pip install python-telegram-bot
   ``` 
4. **Configurazione del bot**
   I parametri di configurazione sono presenti all’interno del file `.env`
5. **Avvio del bot**
   ```bash
   python3 main.py
   ```

## Analisi del Codice
### scraper.py
Il file `scraper.py` contiene il codice per estrapolare gli orari dei bus dal sito dell'ATM e per gestire le informazioni relative alle tratte di interesse.
#### Classes
```python
CLASSES = ["table4", "table5"]
```
Questa variabile contiene le classi CSS utilizzate dal sito ATM per racchiudere gli orari dei bus. Le classi `table4` e `table5` rappresentano le tabelle HTML che contengono le informazioni di interesse. Tuttavia, queste classi potrebbero cambiare nel tempo se il sito subisse aggiornamenti strutturali, pertanto è necessario monitorare e aggiornare queste informazioni in caso di modifiche.

#### Info
```python
INFO = {
    0: {
        "URL": os.getenv("INFO_0_URL"),
        "Departure": os.getenv("INFO_0_DEPARTURE"),
        "Destination": os.getenv("INFO_0_DESTINATION"),
        "Time-to-Arrive": int(os.getenv("INFO_0_TIME_TO_ARRIVE")),
        "buses": json.loads(os.getenv("INFO_0_BUSES"))
    },
    
    1: {
        "URL": os.getenv("INFO_1_URL"),
        "Departure": os.getenv("INFO_1_DEPARTURE"),
        "Destination": os.getenv("INFO_1_DESTINATION"),
        "Time-to-Arrive": int(os.getenv("INFO_1_TIME_TO_ARRIVE")),
        "buses": json.loads(os.getenv("INFO_1_BUSES"))
    }
}
```
`INFO` è un dizionario che contiene i dettagli relativi alle due tratte di interesse (ad esempio, il percorso da casa all'università e viceversa). Le informazioni necessarie vengono caricate dal file `.env`, permettendo una configurazione flessibile e personalizzabile.
- **URL**: La URL della smart pole associata al punto di partenza.
- **Departure**: Nome del punto di partenza.
- **Destination**: Nome del punto di destinazione.
- **Time-to-Arrive**: Minuti necessari per raggiungere la fermata, considerando un passo normale.
- **buses**: Lista delle linee di bus che collegano il punto di partenza al punto di destinazione.

##### Esempio di Configurazione `.env`
```python
INFO_0_URL="https://www.atmmessinaspa.it/smartpoles2.php?palina=XYZ"
INFO_0_DEPARTURE="Stazione"
INFO_0_DESTINATION="Terminal"
INFO_0_TIME_TO_ARRIVE="10"
INFO_0_BUSES='["1", "20", "30B", "40/"]'

INFO_1_URL="https://www.atmmessinaspa.it/smartpoles2.php?palina=ABC"
INFO_1_DEPARTURE="Terminal"
INFO_1_DESTINATION="Stazione"
INFO_1_TIME_TO_ARRIVE="6"
INFO_1_BUSES='["27", "49/"]'
```
Questa configurazione prevede l'inserimento delle informazioni necessarie per il funzionamento del bot. Per la tratta di andata, i dettagli sono identificati con il prefisso `INFO_0_`, mentre per la tratta di ritorno viene utilizzato `INFO_1_`.

#### getRunInfo( )
```python
def getRunInfo(early: int) -> str: 
	if early < -3: return "🔵" 
	elif early <= 0: return "🔴" 
	elif early <= 2: return "🟠" 
	elif early <= 4: return "🟡" 
	else: return "🟢"
```
La funzione `getRunInfo()` è utilizzata per fornire un'indicazione visiva immediata sull'opportunità di raggiungere la fermata in tempo utile, in base al tempo stimato per arrivare. Le indicazioni sono:
- **🔵 (Blu)**: Impossibile raggiungere la fermata in tempo.
- **🔴 (Rosso)**: Si può arrivare giusto in tempo con un passo molto spedito. 
	- (0 minuti di anticipo)
- **🟠 (Arancione)**: È necessario mantenere un passo veloce per arrivare con un paio di minuti di anticipo.
	- (1-2 minuti di anticipo)
- **🟡 (Giallo)**: Si può raggiungere la fermata con calma, ma mantenendo una camminata normale.
	- (3-4 minuti di anticipo)
- **🟢 (Verde)**: Si può raggiungere la fermata senza alcuna fretta.
	- (5+ minuti di anticipo)

### main.py
Il file `main.py` gestisce l'interfaccia con Telegram e le funzionalità di sicurezza del bot.
#### start
```python
async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id != AUTHORIZED_USER_ID:
        logging.warning(f"Unauthorized access attempt by user {user_id}.")
        await update.message.reply_text("❌ Action not allowed.")
        await context.bot.send_message(chat_id=AUTHORIZED_USER_ID, text=f"⚠️ Tentativo di accesso non autorizzato da un utente #{user_id}.")
        return 
```
Questa funzione assicura che solo l'utente autorizzato possa utilizzare il bot. Quando un utente non autorizzato tenta di accedere, il bot invia una notifica all'utente autorizzato con l'ID dell'intruso, bloccando l'accesso a chiunque non sia riconosciuto.

### Configurazione finale del file `.env`
Il file `.env` è fondamentale per il corretto funzionamento del bot e deve contenere i seguenti parametri (i cui valori sono personalizzabili):
```env
AUTHORIZED_USER_ID=123456789  # ID utente Telegram
TOKEN=ABCDEFGHIJKLMNOPQRSTUVWXYZ  # TOKEN bot Telegram

INFO_0_URL="https://www.atmmessinaspa.it/smartpoles2.php?palina=XYZ"
INFO_0_DEPARTURE="Stazione"
INFO_0_DESTINATION="Terminal"
INFO_0_TIME_TO_ARRIVE="10"
INFO_0_BUSES='["1", "20", "30B", "40/"]'

INFO_1_URL="https://www.atmmessinaspa.it/smartpoles2.php?palina=ABC"
INFO_1_DEPARTURE="Terminal"
INFO_1_DESTINATION="Stazione"
INFO_1_TIME_TO_ARRIVE="6"
INFO_1_BUSES='["27", "49/"]'
```

## Limitazioni e possibili sviluppi
Attualmente, UniRideATM è limitato al monitoraggio di una specifica tratta. Questa limitazione è intenzionale e riflette l'obiettivo originale del progetto. Tuttavia, il codice è strutturato in modo da poter essere facilmente esteso e adattato per includere altre tratte, o per monitorare diverse linee e orari.
### Possibili miglioramenti
- **Estensione a più tratte**: con un minimo di adattamento, il bot potrebbe essere configurato per supportare ulteriori tratte e linee.
- **Funzionalità di notifiche avanzate**: implementare un sistema di notifiche che avvisi l'utente in anticipo quando è ora di partire per raggiungere la fermata.

## Licenza
Questo progetto è distribuito sotto la licenza MIT. Per maggiori dettagli, consulta il file `LICENSE` incluso nel repository.
