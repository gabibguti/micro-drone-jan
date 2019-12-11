#include <FastLED.h>

#define LED_PIN_TOP     5
#define LED_PIN_BOTTOM     6
#define NUM_LEDS    30
#define BRIGHTNESS  64
#define OFFSET 2
#define PACKAGE_LED 2
#define GAP_LED 21
#define LED_TYPE    WS2811
#define COLOR_ORDER GRB
CRGB ledsTop[NUM_LEDS];
CRGB ledsBottom[NUM_LEDS];

const CRGB white = CRGB::White;
const CRGB black = CRGB::Black;


//int lightSensorPin1 = A1;        // PIN Light Sensor is connected to
//int lightSensorPin2 = A2;        // PIN Light Sensor is connected to
//int lightSensorPin3 = A3;        // PIN Light Sensor is connected to
int lightSensorPins[4] = {A0, A1, A2, A3};        // PIN Light Sensors
bool lightSensorValues[4] = {false, false, false, false};
int analogValue = 0;


/*void initializeShelf(){
  for(int i=OFFSET; i < NUM_LEDS; i+= PACKAGE_LED + GAP_LED){
    leds[i] = CRGB::White;
    leds[i + 1] = CRGB::Green;
  }
}*/

void setup() {
    delay( 3000 ); // power-up safety delay
    FastLED.addLeds<LED_TYPE, LED_PIN_TOP, COLOR_ORDER>(ledsTop, NUM_LEDS).setCorrection( TypicalLEDStrip );
    FastLED.addLeds<LED_TYPE, LED_PIN_BOTTOM, COLOR_ORDER>(ledsBottom, NUM_LEDS).setCorrection( TypicalLEDStrip );
    FastLED.setBrightness(  BRIGHTNESS );
    //initializeShelf();
    

    Serial.begin(9600);

    
}

String getValue(String data, char separator, int index)
{
    int found = 0;
    int strIndex[] = { 0, -1 };
    int maxIndex = data.length() - 1;

    for (int i = 0; i <= maxIndex && found <= index; i++) {
        if (data.charAt(i) == separator || i == maxIndex) {
            found++;
            strIndex[0] = strIndex[1] + 1;
            strIndex[1] = (i == maxIndex) ? i+1 : i;
        }
    }
    return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
}

void loop()
{
    String texto = Serial.readString();
    texto.trim();
    if (texto != ""){
      String cod = getValue(texto, ' ', 0);
      if (cod == "branco"){
        for( int i = 0; i < NUM_LEDS; i++) {
          ledsTop[i] = CRGB::White;
          ledsBottom[i] = CRGB::White;
        }
      }
      else if (cod == "preto"){
        for( int i = 0; i < NUM_LEDS; i++) {
          ledsTop[i] = CRGB::Black;
          ledsBottom[i] = CRGB::Black;
        }
      }
      /*else if (cod == "inicializa"){
        initializeShelf();
      }*/
      else if (cod == "rainbow"){
        int colorIndex = 0;
        for( int i = 0; i < NUM_LEDS; i++) {
          ledsTop[i] = ColorFromPalette( RainbowColors_p, colorIndex, 255, LINEARBLEND);
          ledsBottom[i] = ColorFromPalette( RainbowColors_p, colorIndex, 255, LINEARBLEND);
          colorIndex += 10;
        }
      }
      else if (cod == "emdia"){
        bool isTop = false;
        if((getValue(texto, ' ', 1).toInt()-1) < 2){
          isTop = true;
        }
        int endereco = ((getValue(texto, ' ', 1).toInt()-1)%2)*(PACKAGE_LED + GAP_LED) + OFFSET;
        if (isTop){
          if (ledsTop[endereco] == white){
            ledsTop[endereco + 1] = CRGB::Green;
          }
        }
        else
        {
          if (ledsBottom[endereco] == white){
            ledsBottom[endereco + 1] = CRGB::Green;
          }
        }
      }
      else if (cod == "ultimodia"){
        bool isTop = false;
        if((getValue(texto, ' ', 1).toInt()-1) < 2){
          isTop = true;
        }
        int endereco = ((getValue(texto, ' ', 1).toInt()-1)%2)*(PACKAGE_LED + GAP_LED) + OFFSET;
        if (isTop){
          if (ledsTop[endereco] == white){
            ledsTop[endereco + 1] = CRGB::Yellow;
          }
        }
        else
        {
          if (ledsBottom[endereco] == white){
            ledsBottom[endereco + 1] = CRGB::Yellow;
          }
        }
      }
      else if (cod == "atraso"){
        bool isTop = false;
        if((getValue(texto, ' ', 1).toInt()-1) < 2){
          isTop = true;
        }
        int endereco = ((getValue(texto, ' ', 1).toInt()-1)%2)*(PACKAGE_LED + GAP_LED) + OFFSET;
        if (isTop){
          if (ledsTop[endereco] == white){
            ledsTop[endereco + 1] = CRGB::Red;
          }
        }
        else
        {
          if (ledsBottom[endereco] == white){
            ledsBottom[endereco + 1] = CRGB::Red;
          }
        }
      }
      /*else if (cod == "retirar"){
        int endereco = (getValue(texto, ' ', 1).toInt()-1)*(PACKAGE_LED + GAP_LED) + OFFSET;
        if (leds[endereco] == white){
          leds[endereco] = CRGB::Black;
          leds[endereco + 1] = CRGB::Black;
        }
      }
      else if (cod == "chegou"){
        String condicao = getValue(texto, ' ', 1);
        int endereco = (getValue(texto, ' ', 2).toInt()-1)*(PACKAGE_LED + GAP_LED) + OFFSET;
        if (leds[endereco] != white)
        {
          if (condicao == "emdia"){
            leds[endereco] = CRGB::White;
            leds[endereco + 1] = CRGB::Green;
          }
          else if (condicao == "ultimodia"){
            leds[endereco] = CRGB::White;
            leds[endereco + 1] = CRGB::Yellow;
          }
          else if (condicao == "atraso"){
            leds[endereco] = CRGB::White;
            leds[endereco + 1] = CRGB::Red;
          }
        }
      }*/
    }
    for(int i=0; i<4; i++){
      analogValue = analogRead(lightSensorPins[i]);
      bool isTop = false;
      if(i < 2){
        isTop = true;
      }
      int endereco = (i%2)*(PACKAGE_LED + GAP_LED) + OFFSET;
      bool isPresent = false;
      String saida = "";
      //Serial.println(analogValue);
      //delay(100); 
      if(analogValue > 900){            
        isPresent = true;
        if(isTop){
          ledsTop[endereco] = CRGB::White;
        }
        else{
          ledsBottom[endereco] = CRGB::White;
        }
      }
      else
      {
        if(isTop){
          ledsTop[endereco] = CRGB::Black;
        }
        else{
          ledsBottom[endereco] = CRGB::Black;
        }
      }
      if (isPresent != lightSensorValues[i]){
        lightSensorValues[i] = isPresent;
        String row = "1";
        if(isTop){
          row = "0";
        }
        if(isPresent){
          saida += "novo " + row + " 0" + String(i % 2);
          Serial.println(saida);
        }
        else{
          saida += "saiu " + row + " 0" + String(i % 2);
          Serial.println(saida);
        }
      }
    }
    FastLED.show();
    FastLED.delay(10);
}
