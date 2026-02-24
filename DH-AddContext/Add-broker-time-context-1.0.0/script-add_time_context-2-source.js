
function transform(publish, context) {

   const unixTime = Math.floor(Date.now() / 1000);
   publish.payload.BrokerIsoTime = unixTime;

   const utcTime = new Date().toISOString();
   publish.payload.BrokerUTCTime = utcTime; 

   return publish; 
};