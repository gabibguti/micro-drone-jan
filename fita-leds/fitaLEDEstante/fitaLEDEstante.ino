#include <FastLED.h>

#define LED_PIN     5
#define NUM_LEDS    30
#define BRIGHTNESS  64
#define PACKAGE_LED 2
#define GAP_LED 5
#define LED_TYPE    WS2811
#define COLOR_ORDER GRB
CRGB leds[NUM_LEDS];

const CRGB white = CRGB::White;
const CRGB black = CRGB::Black;


void initializeShelf(){
  for(int i=0; i < NUM_LEDS; i+= PACKAGE_LED + GAP_LED){
    leds[i] = CRGB::White;
    leds[i + 1] = CRGB::Green;
  }
}

void setup() {
    delay( 3000 ); // power-up safety delay
    FastLED.addLeds<LED_TYPE, LED_PIN, COLOR_ORDER>(leds, NUM_LEDS).setCorrection( TypicalLEDStrip );
    FastLED.setBrightness(  BRIGHTNESS );
    initializeShelf();

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
          leds[i] = CRGB::White;
        }
      }
      else if (cod == "preto"){
        for( int i = 0; i < NUM_LEDS; i++) {
          leds[i] = CRGB::Black;
        }
      }
      else if (cod == "inicializa"){
        initializeShelf();
      }
      else if (cod == "rainbow"){
        int colorIndex = 0;
        for( int i = 0; i < NUM_LEDS; i++) {
          leds[i] = ColorFromPalette( RainbowColors_p, colorIndex, 255, LINEARBLEND);
          colorIndex += 10;
        }
      }
      else if (cod == "emdia"){
        int endereco = (getValue(texto, ' ', 1).toInt()-1)*7;
        if (leds[endereco] == white){
          leds[endereco + 1] = CRGB::Green;
        }
      }
      else if (cod == "ultimodia"){
        int endereco = (getValue(texto, ' ', 1).toInt()-1)*7;
        if (leds[endereco] == white){
          leds[endereco + 1] = CRGB::Yellow;
        }
      }
      else if (cod == "atraso"){
        int endereco = (getValue(texto, ' ', 1).toInt()-1)*7;
        if (leds[endereco] == white){
          leds[endereco + 1] = CRGB::Red;
        }
      }
      else if (cod == "retirar"){
        int endereco = (getValue(texto, ' ', 1).toInt()-1)*7;
        if (leds[endereco] == white){
          leds[endereco] = CRGB::Black;
          leds[endereco + 1] = CRGB::Black;
        }
      }
      else if (cod == "chegou"){
        String condicao = getValue(texto, ' ', 1);
        int endereco = (getValue(texto, ' ', 2).toInt()-1)*7;
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
      }
    }
    FastLED.show();
    FastLED.delay(10);
}
