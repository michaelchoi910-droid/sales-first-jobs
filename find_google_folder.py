#!/usr/bin/env python3
"""
Google Drive 폴더 ID 찾기 도구

이 스크립트는 Google Drive의 폴더 목록을 보여주고
폴더 ID를 쉽게 찾을 수 있도록 도와줍니다.
"""

import os
from dotenv import load_dotenv

load_dotenv()


def list_folders():
    """List all folders in Google Drive"""
    try:
        from src.google_docs_client import GoogleDocsClient

        print("=" * 80)
        print("  📁 Google Drive 폴더 찾기")
        print("=" * 80)
        print()

        print("🔑 Google 인증 중...")
        client = GoogleDocsClient()

        print("📋 Google Drive 폴더 목록 가져오는 중...")
        print()

        # List folders using Drive API
        results = client.drive_service.files().list(
            q="mimeType='application/vnd.google-apps.folder' and trashed=false",
            pageSize=50,
            fields="files(id, name, parents, createdTime, modifiedTime)"
        ).execute()

        folders = results.get('files', [])

        if not folders:
            print("⚠️  폴더를 찾을 수 없습니다.")
            return

        print(f"✅ {len(folders)}개의 폴더를 찾았습니다:")
        print()
        print("=" * 80)

        for i, folder in enumerate(folders, 1):
            print(f"{i:2d}. 📁 {folder['name']}")
            print(f"    ID: {folder['id']}")
            if 'parents' in folder:
                print(f"    부모 폴더: {folder['parents'][0]}")
            print()

        print("=" * 80)
        print()
        print("💡 사용 방법:")
        print("   1. 위에서 원하는 폴더의 ID 복사")
        print("   2. config.py 파일 열기")
        print("   3. GOOGLE_DRIVE_FOLDER_ID에 붙여넣기")
        print()
        print("예시:")
        print(f"   GOOGLE_DRIVE_FOLDER_ID = \"{folders[0]['id']}\"")
        print()

        # Interactive selection
        print("=" * 80)
        response = input("config.py에 자동으로 설정할까요? 폴더 번호 입력 (엔터=취소): ").strip()

        if response and response.isdigit():
            idx = int(response) - 1
            if 0 <= idx < len(folders):
                selected = folders[idx]
                update_config(selected['id'], selected['name'])
            else:
                print("❌ 잘못된 번호입니다.")
        else:
            print("취소되었습니다.")

    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("💡 Google Cloud 설정이 필요합니다:")
        print("   python src/main.py --setup-google")


def update_config(folder_id, folder_name):
    """Update config.py with folder ID"""
    try:
        with open('config.py', 'r', encoding='utf-8') as f:
            content = f.read()

        # Replace the GOOGLE_DRIVE_FOLDER_ID line
        import re
        pattern = r'GOOGLE_DRIVE_FOLDER_ID = "[^"]*"'
        replacement = f'GOOGLE_DRIVE_FOLDER_ID = "{folder_id}"  # {folder_name}'

        if re.search(pattern, content):
            new_content = re.sub(pattern, replacement, content)
        else:
            # If not found, try empty string pattern
            pattern = r'GOOGLE_DRIVE_FOLDER_ID = ""'
            replacement = f'GOOGLE_DRIVE_FOLDER_ID = "{folder_id}"  # {folder_name}'
            new_content = re.sub(pattern, replacement, content)

        with open('config.py', 'w', encoding='utf-8') as f:
            f.write(new_content)

        print()
        print("=" * 80)
        print(f"✅ config.py가 업데이트되었습니다!")
        print("=" * 80)
        print(f"   폴더: {folder_name}")
        print(f"   ID: {folder_id}")
        print()
        print("이제 auto_monitor.py를 실행하면 이 폴더에 문서가 생성됩니다!")
        print()

    except Exception as e:
        print(f"❌ config.py 업데이트 실패: {e}")


def find_folder_by_url():
    """Find folder ID from Google Drive URL"""
    print("=" * 80)
    print("  🔗 URL에서 폴더 ID 추출")
    print("=" * 80)
    print()
    print("Google Drive 폴더 URL을 붙여넣으세요:")
    print("예시: https://drive.google.com/drive/folders/1a2b3c4d5e6f7g8h9i0j")
    print()

    url = input("URL: ").strip()

    if not url:
        print("취소되었습니다.")
        return

    # Extract folder ID from URL
    import re
    match = re.search(r'/folders/([a-zA-Z0-9_-]+)', url)

    if match:
        folder_id = match.group(1)
        print()
        print("=" * 80)
        print("✅ 폴더 ID를 찾았습니다!")
        print("=" * 80)
        print(f"   ID: {folder_id}")
        print()

        response = input("config.py에 설정할까요? (y/N): ").strip().lower()
        if response == 'y':
            update_config(folder_id, "Selected folder")
    else:
        print("❌ URL에서 폴더 ID를 찾을 수 없습니다.")
        print("   올바른 Google Drive 폴더 URL인지 확인해주세요.")


def main():
    """Main function"""
    print("=" * 80)
    print("  🔍 Google Drive 폴더 ID 찾기 도구")
    print("=" * 80)
    print()
    print("선택하세요:")
    print("  1. Google Drive에서 폴더 목록 보기 (추천)")
    print("  2. URL에서 폴더 ID 추출")
    print()

    choice = input("선택 (1/2): ").strip()

    print()

    if choice == "1":
        list_folders()
    elif choice == "2":
        find_folder_by_url()
    else:
        print("취소되었습니다.")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n취소되었습니다.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
