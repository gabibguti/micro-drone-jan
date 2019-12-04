int ldrValor = 0; //Valor lido do LDR
int valor =0;
int ldrPin = 0;

void setup() {

 Serial.begin(9600); //Inicia a comunicação serial
}
 
void loop() {
 ///ler o valor do LDR
 ldrValor = analogRead(ldrPin); //O valor lido será entre 0 e 1023
 
 //se o valor lido for maior que 500, liga o led
 if (ldrValor>= 500) valor = 1;
 // senão, apaga o led
 else valor = 0;
 
 //imprime o valor lido do LDR no monitor serial
 Serial.println(ldrValor);
 delay(100);
}
