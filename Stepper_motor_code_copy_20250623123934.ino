float k = 400;
float f = 30;

void setup() {
  pinMode(2,OUTPUT);
  pinMode(3,OUTPUT);
  digitalWrite(2,HIGH);
  // put your setup code here, to run once:

}

void loop() {
  digitalWrite(3,LOW);
  digitalWrite(3,HIGH);
  delay((10*k)/(32*f));
  // put your main code here, to run repeatedly:

}
