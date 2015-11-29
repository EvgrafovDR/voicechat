class CreateMessages < ActiveRecord::Migration
  def change
    create_table :messages do |t|
      t.integer :user_id_from
      t.integer :user_id_to
      t.string :content

      t.timestamps
    end
    add_index :messages, [:user_id_from, :created_at]
  end
end
