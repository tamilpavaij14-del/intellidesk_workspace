<<<<<<< HEAD
"use client";

import { createClient } from "@/utils/supabase/client";

export default function LoginPage() {
  const supabase = createClient();
  console.log("SUPABASE URL:", process.env.NEXT_PUBLIC_SUPABASE_URL);

  async function signInWithGoogle() {
    await supabase.auth.signInWithOAuth({
      provider: "google",
      options: { redirectTo: `${location.origin}/auth/callback` },
    });
  }

  return (
    <main style={{ padding: 32 }}>
      <h1>Sign in to IntelliDesk</h1>
      <button onClick={signInWithGoogle} style={{ padding: 10 }}>
        Sign in with Google
      </button>
    </main>
  );
}
=======
export default function Page() {
  return (
    <div>
      <h1>IntelliDesk</h1>
    </div>
  );
}
>>>>>>> 0a2ced1229742708dd9d8ef4fb170099e22dc9f9
