import * as admin from 'firebase-admin';

const serviceAccount = require('./credentials/calculoidf-firebase-adminsdk-lc7id-420d8fac04.json');

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  storageBucket: "calculoidf.appspot.com"
});

const bucket = admin.storage().bucket();

export default bucket;
