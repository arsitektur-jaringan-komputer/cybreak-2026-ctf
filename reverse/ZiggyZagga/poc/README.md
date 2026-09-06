# ZiggyZagga - Proof of Concept

> Cybreak 2026 - Reverse - Medium - DJumanto

## Unpacking the App
initially the application is heavily packed with DPT-Shell protection. So any class and activity will be stripped and only left initial classes. However, the AndroidManifest.xml still giving us the big picture of the application.


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

Seems like there's 2 activity that accept deeplink with their own path, and a provider that has ``grantUriPermissions=true`` which allowed us to read internal files. However it's not accessible directly from outside. So we need a way where the application giving access to the uri permissions to an intent.

So what we do next because we don't know how the logic works, we need to unpack it. Looking at github adn some youtube videos will return you various method to unpack the dpt shell.

## Attack Path after Unpacking
As always, to solve a problem, i always use the backtrack method on how do we get the flag to where can we supplied the initial data. Since the flag located in internal files, we need to find out how we can arbitrary read internal files. Luckily, the bless activity gives the clue clearly

### Bless Activity Intent Redirection
```java
if (getIntent().getBooleanExtra("WeatherReport", false) && zHandleIt) {
    setResult(-1, getIntent());
    finish();
    return;
}
return;
```

It returns any intent data information without sanitize it, however there's some checks they did before reaching it, which is a boolean ``WeatherReport`` extra, and zHandleIt value, which returned from handleIt() function

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
