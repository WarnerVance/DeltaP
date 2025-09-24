#!/usr/bin/env python3
"""
Test script for the point approval system.
This script tests the database schema changes and basic functionality.
"""

import sqlite3
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_database_schema():
    """Test that the database schema has been updated correctly."""
    print("Testing database schema...")
    
    # Get database file name from environment
    db_file = os.getenv('CSV_NAME', 'pledge_points.db')
    
    # Connect to database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Check if new columns exist
    cursor.execute("PRAGMA table_info(Points)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    required_columns = ['id', 'approval_status', 'approved_by', 'approval_timestamp']
    missing_columns = [col for col in required_columns if col not in column_names]
    
    if missing_columns:
        print(f"❌ Missing columns: {missing_columns}")
        return False
    else:
        print("✅ All required columns present")
    
    # Test inserting a sample point with approval status
    test_point = (
        datetime.now().isoformat(),
        10,
        "TestPledge",
        "TestBrother",
        "Test comment",
        "pending"
    )
    
    try:
        cursor.execute("""
            INSERT INTO Points (Time, PointChange, Pledge, Brother, Comment, approval_status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, test_point)
        conn.commit()
        print("✅ Successfully inserted test point with pending status")
        
        # Get the ID of the inserted point
        cursor.execute("SELECT id FROM Points WHERE Brother = 'TestBrother' ORDER BY id DESC LIMIT 1")
        point_id = cursor.fetchone()[0]
        print(f"✅ Test point inserted with ID: {point_id}")
        
        # Test updating approval status
        cursor.execute("""
            UPDATE Points 
            SET approval_status = 'approved', 
                approved_by = 'TestApprover', 
                approval_timestamp = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), point_id))
        conn.commit()
        print("✅ Successfully updated approval status")
        
        # Test querying approved points
        cursor.execute("SELECT COUNT(*) FROM Points WHERE approval_status = 'approved'")
        approved_count = cursor.fetchone()[0]
        print(f"✅ Found {approved_count} approved points")
        
        # Test querying pending points
        cursor.execute("SELECT COUNT(*) FROM Points WHERE approval_status = 'pending'")
        pending_count = cursor.fetchone()[0]
        print(f"✅ Found {pending_count} pending points")
        
        # Clean up test data
        cursor.execute("DELETE FROM Points WHERE Brother = 'TestBrother'")
        conn.commit()
        print("✅ Cleaned up test data")
        
    except Exception as e:
        print(f"❌ Error during database operations: {e}")
        return False
    finally:
        conn.close()
    
    return True

def test_point_processing():
    """Test that point processing functions work with the new schema."""
    print("\nTesting point processing functions...")
    
    try:
        from PledgePoints.messages import add_new_points, get_old_points
        from PledgePoints.pledges import get_pledge_points
        
        # Get database file name
        db_file = os.getenv('CSV_NAME', 'pledge_points.db')
        
        # Test adding new points
        test_points = [
            (datetime.now(), 5, "TestPledge1", "TestBrother1", "Test comment 1"),
            (datetime.now(), -3, "TestPledge2", "TestBrother2", "Test comment 2")
        ]
        
        conn = sqlite3.connect(db_file)
        add_new_points(conn, test_points)
        print("✅ Successfully added test points")
        
        # Test getting old points (should only return approved points)
        conn = sqlite3.connect(db_file)
        old_points = get_old_points(conn)
        print(f"✅ Retrieved {len(old_points)} approved points")
        
        # Test getting pledge points
        conn = sqlite3.connect(db_file)
        pledge_df = get_pledge_points(conn)
        print(f"✅ Retrieved pledge points DataFrame with {len(pledge_df)} rows")
        
        # Clean up
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Points WHERE Brother LIKE 'TestBrother%'")
        conn.commit()
        conn.close()
        print("✅ Cleaned up test data")
        
    except Exception as e:
        print(f"❌ Error during point processing test: {e}")
        return False
    
    return True

def main():
    """Run all tests."""
    print("🧪 Testing Point Approval System\n")
    
    # Test database schema
    schema_ok = test_database_schema()
    
    # Test point processing
    processing_ok = test_point_processing()
    
    print("\n" + "="*50)
    if schema_ok and processing_ok:
        print("🎉 All tests passed! The approval system is ready to use.")
        print("\nNew commands available:")
        print("- /view_pending_points - View all pending submissions")
        print("- /approve_points <ids> - Approve points by ID (Executive Board only)")
        print("- /reject_points <ids> - Reject points by ID (Executive Board only)")
        print("- /view_point_details <id> - View detailed point information")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    return schema_ok and processing_ok

if __name__ == "__main__":
    main()
