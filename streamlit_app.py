import streamlit as st
from supabase import create_client, Client

# --- 1. Supabaseへの接続設定 ---
# st.secrets から URL と Key を読み込む
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]

# クライアントの作成（キャッシュを使って再接続を防ぐ）
@st.cache_resource
def init_connection():
    return create_client(url, key)

supabase: Client = init_connection()

# --- 2. データベース操作関数 ---

# Todoを取得する
def get_todos():
    # created_at の降順（新しい順）で取得
    response = supabase.table("todos").select("*").order("created_at", desc=True).execute()
    return response.data

# Todoを追加する
def add_todo(task_name):
    supabase.table("todos").insert({"task": task_name}).execute()

# Todoを削除する
def delete_todo(todo_id):
    supabase.table("todos").delete().eq("id", todo_id).execute()

# タスクの完了状態を切り替える（更新）
def toggle_complete(todo_id, current_status):
    supabase.table("todos").update({"is_complete": not current_status}).eq("id", todo_id).execute()


# --- 3. アプリの画面構成 ---

st.title("📝 Supabase Todo App")
st.write("データはクラウド(Supabase)に保存されるため、アプリを閉じても消えません。")

# --- 新規タスク入力フォーム ---
with st.form("todo_form", clear_on_submit=True):
    new_task = st.text_input("新しいタスクを入力してください")
    submitted = st.form_submit_button("追加")
    
    if submitted and new_task:
        add_todo(new_task)
        st.success(f"追加しました: {new_task}")
        st.rerun() # 画面を更新してリストを再読み込み

st.divider()

# --- Todoリストの表示 ---
todos = get_todos()

if not todos:
    st.info("タスクはまだありません。")
else:
    for todo in todos:
        # カードのような見た目で表示
        col1, col2, col3 = st.columns([0.1, 0.7, 0.2])
        
        # 完了チェックボックス (完了/未完了の切り替え)
        with col1:
            is_done = st.checkbox(
                "完了", 
                value=todo["is_complete"], 
                key=f"check_{todo['id']}",
                label_visibility="collapsed",
                on_change=toggle_complete,
                args=(todo["id"], todo["is_complete"])
            )
        
        # タスク名表示
        with col2:
            if todo["is_complete"]:
                st.markdown(f"~~{todo['task']}~~") # 完了なら取り消し線
            else:
                st.write(todo["task"])
        
        # 削除ボタン
        with col3:
            if st.button("削除", key=f"del_{todo['id']}"):
                delete_todo(todo["id"])
                st.rerun()
